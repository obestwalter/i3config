"""Status bar and built-in Qtile widgets replicating i3bar + py3status.

Converted from:
- config.d/i3bar.simple.conf
- config.d/i3bar.full.conf
- py3status/ custom modules
"""

from __future__ import annotations

import platform
import re
import shutil
import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from libqtile import bar, qtile, widget
from libqtile.config import Screen

from colors import ColorTheme
from groups import WORKSPACE_SPECS, format_window_title
from settings import (
    BAR_SEPARATOR,
    BIN_DIR,
    FONT_FAMILY,
    get_active_theme,
    get_bar_font_size,
    get_bar_position,
)

PROC_STAT: Final[Path] = Path("/proc/stat")
PROC_MEMINFO: Final[Path] = Path("/proc/meminfo")
PROC_WIRELESS: Final[Path] = Path("/proc/net/wireless")
PROC_NET_ROUTE: Final[Path] = Path("/proc/net/route")
SYS_THERMAL_DIR: Final[Path] = Path("/sys/class/thermal")
SYS_POWER_SUPPLY_DIR: Final[Path] = Path("/sys/class/power_supply")
BATTERY_BLOCKS: Final[str] = "_▁▂▃▄▅▆▇█"


# ---------------------------------------------------------------------------
# Pure-Python Status Poller (zero external pip dependencies required)
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class SystemStatusPoller:
    """Encapsulates stateful and stateless system polling for status bar widgets."""

    prev_cpu_times: tuple[int, int] = field(default=(0, 0))

    def poll_sysdata(self) -> str:
        """Poll CPU usage %, CPU temperature, and RAM usage % (`sysdata` in py3status)."""
        cpu_pct = self._read_cpu_percent()
        mem_pct = self._read_memory_percent()
        temp_str = self._read_temperature()
        return f" {cpu_pct:.0f}%{temp_str}  {mem_pct:.0f}%"

    def _read_cpu_percent(self) -> float:
        try:
            first_line = PROC_STAT.read_text(encoding="utf-8").splitlines()[0]
            fields = [int(x) for x in first_line.split()[1:]]
            idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
            total = sum(fields)
            prev_total, prev_idle = self.prev_cpu_times
            diff_total = total - prev_total
            diff_idle = idle - prev_idle
            self.prev_cpu_times = (total, idle)
            if diff_total > 0 and prev_total > 0:
                return 100.0 * (diff_total - diff_idle) / diff_total
        except (OSError, ValueError, IndexError):
            pass
        return 0.0

    @staticmethod
    def _read_memory_percent() -> float:
        try:
            mem_info: dict[str, int] = {}
            for line in PROC_MEMINFO.read_text(encoding="utf-8").splitlines():
                parts = line.split(":")
                if len(parts) == 2:
                    mem_info[parts[0].strip()] = int(parts[1].strip().split()[0])
            total_mem = mem_info.get("MemTotal", 0)
            avail_mem = mem_info.get("MemAvailable", mem_info.get("MemFree", 0))
            if total_mem > 0:
                return 100.0 * (total_mem - avail_mem) / total_mem
        except (OSError, ValueError, IndexError):
            pass
        return 0.0

    @staticmethod
    def _read_temperature() -> str:
        try:
            temps = [
                raw / 1000.0
                for tz in sorted(SYS_THERMAL_DIR.glob("thermal_zone*/temp"))
                if (raw := int(tz.read_text(encoding="utf-8").strip())) > 1000
            ]
            if temps:
                return f" {sum(temps) / len(temps):.0f}°C"
        except (OSError, ValueError):
            pass
        return ""

    @staticmethod
    def poll_wifi() -> str:
        """Poll WiFi SSID and signal % (`wifi` module in i3bar.full.conf)."""
        try:
            lines = PROC_WIRELESS.read_text(encoding="utf-8").splitlines()[2:]
            if not lines:
                return ""
            parts = lines[0].split()
            iface = parts[0].rstrip(":")
            quality = float(parts[2].rstrip("."))
            signal_pct = min(100, int(round(quality * 100.0 / 70.0)))

            ssid = ""
            try:
                ssid = (
                    subprocess.check_output(
                        ["iwgetid", "-r"], stderr=subprocess.DEVNULL, timeout=1
                    )
                    .decode("utf-8")
                    .strip()
                )
            except (OSError, subprocess.SubprocessError):
                out = (
                    subprocess.check_output(
                        ["iw", "dev", iface, "link"],
                        stderr=subprocess.DEVNULL,
                        timeout=1,
                    )
                    .decode("utf-8")
                )
                if match := re.search(r"SSID:\s*(.+)", out):
                    ssid = match.group(1).strip()

            return f"{ssid}  {signal_pct}%" if ssid else f" {signal_pct}%"
        except (OSError, ValueError, IndexError, subprocess.SubprocessError):
            return ""

    @staticmethod
    def poll_diskdata() -> str:
        """Poll root filesystem usage (`diskdata` in i3bar.full.conf)."""
        try:
            usage = shutil.disk_usage("/")
            used_pct = (usage.used / usage.total) * 100.0 if usage.total else 0.0
            return f" [/dev/mapper/cryptroot]{used_pct:.1f}%"
        except OSError:
            return " N/A"

    @staticmethod
    def poll_online_status() -> str:
        """Check whether default route / internet is reachable (`online_status` in i3bar.full.conf)."""
        try:
            for line in PROC_NET_ROUTE.read_text(encoding="utf-8").splitlines()[1:]:
                fields = line.strip().split()
                if len(fields) >= 2 and fields[1] == "00000000":
                    return "●"
        except OSError:
            pass
        try:
            with socket.create_connection(("1.1.1.1", 53), timeout=0.5):
                return "●"
        except OSError:
            return "○"

    @staticmethod
    def poll_volume() -> str:
        """Poll default sink volume & mute state (`volume_status` in i3bar.full.conf)."""
        try:
            mute_out = (
                subprocess.check_output(
                    ["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                    stderr=subprocess.DEVNULL,
                    timeout=1,
                )
                .decode("utf-8")
                .strip()
            )
            if "yes" in mute_out.lower():
                return " "

            vol_out = (
                subprocess.check_output(
                    ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                    stderr=subprocess.DEVNULL,
                    timeout=1,
                )
                .decode("utf-8")
                .strip()
            )
            if match := re.search(r"(\d+)%", vol_out):
                return f" {match.group(1)}%"
        except (OSError, subprocess.SubprocessError):
            pass
        return " --%"

    @staticmethod
    def poll_battery() -> str:
        """Poll battery level, block icon, and remaining time (`battery_level` in i3bar.full.conf)."""
        try:
            bats = sorted(SYS_POWER_SUPPLY_DIR.glob("BAT*"))
            if not bats:
                return ""
            capacities = [
                int(cap_file.read_text(encoding="utf-8").strip())
                for bat in bats
                if (cap_file := bat / "capacity").is_file()
            ]
            if not capacities:
                return ""
            pct = min(100, max(0, int(round(sum(capacities) / len(capacities)))))
            block_idx = min(
                len(BATTERY_BLOCKS) - 1,
                int(round(pct * (len(BATTERY_BLOCKS) - 1) / 100.0)),
            )
            icon = BATTERY_BLOCKS[block_idx]

            time_rem = ""
            try:
                acpi_out = (
                    subprocess.check_output(
                        ["acpi", "-b"], stderr=subprocess.DEVNULL, timeout=1
                    )
                    .decode("utf-8")
                    .strip()
                )
                if match := re.search(r"(\d{2}:\d{2}):\d{2}", acpi_out):
                    time_rem = f" {match.group(1)}"
            except (OSError, subprocess.SubprocessError):
                pass

            return f" {pct}% {icon}{time_rem}"
        except (OSError, ValueError):
            return ""


POLLER: Final[SystemStatusPoller] = SystemStatusPoller()


# ---------------------------------------------------------------------------
# Widget & Bar Builders
# ---------------------------------------------------------------------------
def _format_tasklist_title(text: str) -> str:
    """Resolve the window in the current group matching `text` and prefix its icon."""
    try:
        if qtile and qtile.current_group:
            for win in qtile.current_group.windows:
                if win.name == text:
                    return format_window_title(win, text)
        if qtile and qtile.current_window:
            return format_window_title(qtile.current_window, text)
    except Exception:
        pass
    return text


def _sep(
    theme: ColorTheme, screenshot_cb: dict[str, Any], fontsize: int
) -> widget.TextBox:
    """Create the ` ║ ` separator matching i3bar's `separator_symbol`."""
    return widget.TextBox(
        text=BAR_SEPARATOR,
        foreground=theme.focused_separator,
        background=theme.background,
        padding=0,
        fontsize=fontsize,
        mouse_callbacks=screenshot_cb,
    )


def build_widgets(*, primary: bool = True) -> list[Any]:
    """Build the widget list for the primary or secondary screen."""
    theme = get_active_theme()
    bar_font_size = get_bar_font_size()
    visible_groups = [spec.name for spec in WORKSPACE_SPECS]

    # Right-clicking anywhere on the bar (unless overridden by a specific widget)
    # runs screenshot-and-gwenview.sh, matching `bindsym --release button3` in i3bar.simple.conf
    screenshot_script = str(BIN_DIR / "screenshot-and-gwenview.sh")
    bar_right_click: dict[str, Any] = {
        "Button3": lambda: qtile.cmd_spawn(screenshot_script),
    }

    uname_info = platform.uname()
    uname_text = f"{uname_info.node}  {uname_info.release}"

    widgets: list[Any] = [
        # Workspaces (GroupBox)
        widget.GroupBox(
            font=FONT_FAMILY,
            fontsize=bar_font_size,
            visible_groups=visible_groups,
            margin_y=3,
            margin_x=0,
            padding_y=4,
            padding_x=6,
            borderwidth=2,
            active=theme.watxt,
            inactive=theme.witxt,
            rounded=False,
            highlight_method="block",
            this_current_screen_border=theme.wfbg,
            this_screen_border=theme.wabg,
            other_current_screen_border=theme.wfbg,
            other_screen_border=theme.wabg,
            block_highlight_text_color=theme.wftxt,
            urgent_alert_method="block",
            urgent_border=theme.wubg,
            urgent_text=theme.wutxt,
            background=theme.background,
            disable_drag=True,
            use_mouse_wheel=False,  # Matches `bindsym button4 nop` / `button5 nop`
            mouse_callbacks=bar_right_click,
        ),
        # Active KeyChord / Mode indicator (`binding_mode` in i3bar)
        widget.Chord(
            font=FONT_FAMILY,
            fontsize=bar_font_size,
            background=theme.bmbg,
            foreground=theme.bmtxt,
            padding=8,
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # Window tabs for the current workspace (emulates i3's tabbed title bars with icons)
        widget.TaskList(
            font=FONT_FAMILY,
            fontsize=max(8, bar_font_size - 1),
            background=theme.background,
            foreground=theme.cftxt,
            border=theme.cfbg,
            unfocused_border=theme.cubg,
            urgent_border=theme.curbg,
            highlight_method="block",
            markup_focused=f"<span foreground='{theme.cftxt}'>{{}}</span>",
            markup_normal=f"<span foreground='{theme.cutxt}'>{{}}</span>",
            icon_size=0,  # Uses FontAwesome glyphs from format_window_title
            parse_text=_format_tasklist_title,
            padding_x=8,
            padding_y=3,
            margin_x=2,
            margin_y=2,
            rounded=False,
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 1. sysdata (CPU, Temp, RAM)
        widget.GenPollText(
            func=POLLER.poll_sysdata,
            update_interval=2,
            fontsize=bar_font_size,
            foreground=theme.status_good,
            background=theme.background,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("xfce4-terminal -T GLANCES -e 'glances'"),
                "Button3": lambda: qtile.cmd_spawn("xfce4-terminal -T HTOP -e 'htop'"),
            },
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 2. wifi
        widget.GenPollText(
            func=POLLER.poll_wifi,
            update_interval=5,
            fontsize=bar_font_size,
            foreground=theme.status_good,
            background=theme.background,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("networkmanager_dmenu"),
                "Button3": lambda: qtile.cmd_spawn(screenshot_script),
            },
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 3. uname ({node}  {release})
        widget.TextBox(
            text=uname_text,
            fontsize=bar_font_size,
            foreground=theme.status_color,
            background=theme.background,
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 4. diskdata
        widget.GenPollText(
            func=POLLER.poll_diskdata,
            update_interval=30,
            fontsize=bar_font_size,
            foreground=theme.status_color,
            background=theme.background,
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 5. online_status
        widget.GenPollText(
            func=POLLER.poll_online_status,
            update_interval=5,
            fontsize=bar_font_size,
            foreground=theme.status_good,
            background=theme.background,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("xfce4-terminal -e 'nmtui-connect'"),
                "Button3": lambda: qtile.cmd_spawn("xfce4-terminal -e 'nmtui-edit'"),
            },
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 6. volume_status
        widget.GenPollText(
            func=POLLER.poll_volume,
            update_interval=1,
            fontsize=bar_font_size,
            foreground=theme.status_color,
            background=theme.background,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(
                    "pactl set-sink-mute @DEFAULT_SINK@ toggle"
                ),
                "Button2": lambda: qtile.cmd_spawn("pkill quodlibet"),
                "Button3": lambda: qtile.cmd_spawn("quodlibet --run --play-pause"),
                "Button4": lambda: qtile.cmd_spawn(
                    "pactl set-sink-volume @DEFAULT_SINK@ +1%"
                ),
                "Button5": lambda: qtile.cmd_spawn(
                    "pactl set-sink-volume @DEFAULT_SINK@ -1%"
                ),
            },
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 7. battery_level
        widget.GenPollText(
            func=POLLER.poll_battery,
            update_interval=5,
            fontsize=bar_font_size,
            foreground=theme.status_good,
            background=theme.background,
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click, bar_font_size),
        # 8. tztime local
        widget.Clock(
            format=" %a %d.%m  %H:%M",
            fontsize=bar_font_size,
            foreground=theme.status_color,
            background=theme.background,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(
                    "firefox https://calendar.google.com/calendar/render#main_7%7Cmonth"
                ),
                "Button3": lambda: qtile.cmd_spawn(screenshot_script),
            },
        ),
    ]

    # Systray only on primary monitor (`tray_output primary`, `tray_padding 1`)
    if primary:
        widgets.extend(
            [
                _sep(theme, bar_right_click, bar_font_size),
                widget.Systray(
                    background=theme.background,
                    padding=1,
                ),
            ]
        )

    return widgets


def build_screens() -> list[Screen]:
    """Build Screen configurations for all connected monitors (`id all-monitors`)."""
    theme = get_active_theme()
    position = get_bar_position()  # 'bottom' or 'top'
    bar_font_size = get_bar_font_size()
    # Scale bar height proportionally with the bar font size so glyphs never clip
    bar_height = max(24, int(round(bar_font_size * 1.85)))

    primary_bar = bar.Bar(
        build_widgets(primary=True),
        size=bar_height,
        background=theme.background,
    )
    secondary_bar = bar.Bar(
        build_widgets(primary=False),
        size=bar_height,
        background=theme.background,
    )

    return [
        Screen(**{position: primary_bar}),
        Screen(**{position: secondary_bar}),
    ]
