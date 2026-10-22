"""Status bar and built-in Qtile widgets replicating i3bar + py3status.

Converted from:
- config.d/i3bar.simple.conf
- config.d/i3bar.full.conf
- py3status/ custom modules
"""

import os
import platform
import re
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from libqtile import bar, qtile, widget
from libqtile.config import Screen

from groups import WORKSPACE_DEFS, format_window_title
from settings import (
    BAR_FONT_SIZE,
    BAR_SEPARATOR,
    BIN_DIR,
    FONT_FAMILY,
    get_active_theme,
    get_bar_position,
)


# ---------------------------------------------------------------------------
# Pure-Python status pollers (zero external pip dependencies required)
# ---------------------------------------------------------------------------
_prev_cpu_times: tuple[int, int] = (0, 0)


def _poll_sysdata() -> str:
    """Poll CPU usage %, load avg, and CPU temperature (`sysdata` / `cpu_usage` in py3status)."""
    global _prev_cpu_times
    cpu_pct = 0.0
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            fields = [int(x) for x in f.readline().split()[1:]]
        idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
        total = sum(fields)
        prev_total, prev_idle = _prev_cpu_times
        diff_total = total - prev_total
        diff_idle = idle - prev_idle
        if diff_total > 0 and prev_total > 0:
            cpu_pct = 100.0 * (diff_total - diff_idle) / diff_total
        _prev_cpu_times = (total, idle)
    except Exception:
        pass

    # Memory usage %
    mem_pct = 0.0
    try:
        mem_info: Dict[str, int] = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = int(parts[1].strip().split()[0])
                    mem_info[key] = val
        total_mem = mem_info.get("MemTotal", 0)
        avail_mem = mem_info.get("MemAvailable", mem_info.get("MemFree", 0))
        if total_mem > 0:
            mem_pct = 100.0 * (total_mem - avail_mem) / total_mem
    except Exception:
        pass

    # Thermal zone temperature (if available)
    temp_str = ""
    try:
        thermal_zones = sorted(Path("/sys/class/thermal").glob("thermal_zone*/temp"))
        temps = []
        for tz in thermal_zones:
            raw = int(tz.read_text(encoding="utf-8").strip())
            if raw > 1000:
                temps.append(raw / 1000.0)
        if temps:
            temp_str = f" {sum(temps) / len(temps):.0f}°C"
    except Exception:
        pass

    return f" {cpu_pct:.0f}%{temp_str}  {mem_pct:.0f}%"


def _poll_wifi() -> str:
    """Poll WiFi SSID and signal % (`wifi` module in i3bar.full.conf)."""
    try:
        # Read /proc/net/wireless for link quality
        with open("/proc/net/wireless", "r", encoding="utf-8") as f:
            lines = f.readlines()[2:]
        if not lines:
            return ""
        parts = lines[0].split()
        iface = parts[0].rstrip(":")
        quality = float(parts[2].rstrip("."))
        signal_pct = min(100, int(round(quality * 100.0 / 70.0)))

        # Get SSID via iwgetid or iw
        ssid = ""
        try:
            ssid = (
                subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL, timeout=1)
                .decode("utf-8")
                .strip()
            )
        except Exception:
            out = (
                subprocess.check_output(
                    ["iw", "dev", iface, "link"], stderr=subprocess.DEVNULL, timeout=1
                )
                .decode("utf-8")
            )
            m = re.search(r"SSID:\s*(.+)", out)
            if m:
                ssid = m.group(1).strip()

        if ssid:
            return f"{ssid}  {signal_pct}%"
        return f" {signal_pct}%"
    except Exception:
        return ""


def _poll_diskdata() -> str:
    """Poll root filesystem usage (`diskdata` in i3bar.full.conf)."""
    try:
        usage = shutil.disk_usage("/")
        used_pct = (usage.used / usage.total) * 100.0 if usage.total else 0.0
        return f" [/dev/mapper/cryptroot]{used_pct:.1f}%"
    except Exception:
        return " N/A"


def _poll_online_status() -> str:
    """Check whether default route / internet is reachable (`online_status` in i3bar.full.conf)."""
    try:
        with open("/proc/net/route", "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                fields = line.strip().split()
                if len(fields) >= 2 and fields[1] == "00000000":
                    return "●"
    except Exception:
        pass
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=0.5).close()
        return "●"
    except Exception:
        return "○"


def _poll_volume() -> str:
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
        m = re.search(r"(\d+)%", vol_out)
        if m:
            return f" {m.group(1)}%"
    except Exception:
        pass
    return " --%"


def _poll_battery() -> str:
    """Poll battery level, block icon, and remaining time (`battery_level` in i3bar.full.conf)."""
    blocks = "_▁▂▃▄▅▆▇█"
    try:
        bats = sorted(Path("/sys/class/power_supply").glob("BAT*"))
        if not bats:
            return ""
        capacities = []
        status = "Unknown"
        for bat in bats:
            cap_file = bat / "capacity"
            stat_file = bat / "status"
            if cap_file.exists():
                capacities.append(int(cap_file.read_text(encoding="utf-8").strip()))
            if stat_file.exists():
                st = stat_file.read_text(encoding="utf-8").strip()
                if st in ("Charging", "Discharging"):
                    status = st

        if not capacities:
            return ""
        pct = min(100, max(0, int(round(sum(capacities) / len(capacities)))))
        block_idx = min(len(blocks) - 1, int(round(pct * (len(blocks) - 1) / 100.0)))
        icon = blocks[block_idx]

        # Optional time remaining from `acpi` if installed
        time_rem = ""
        try:
            acpi_out = (
                subprocess.check_output(["acpi", "-b"], stderr=subprocess.DEVNULL, timeout=1)
                .decode("utf-8")
                .strip()
            )
            m = re.search(r"(\d{2}:\d{2}):\d{2}", acpi_out)
            if m:
                time_rem = f" {m.group(1)}"
        except Exception:
            pass

        return f" {pct}% {icon}{time_rem}"
    except Exception:
        return ""


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


def _sep(theme: Dict[str, str], screenshot_cb: Dict[str, Any]) -> widget.TextBox:
    """Create the ` ║ ` separator matching i3bar's `separator_symbol`."""
    return widget.TextBox(
        text=BAR_SEPARATOR,
        foreground=theme["focused_separator"],
        background=theme["background"],
        padding=0,
        fontsize=BAR_FONT_SIZE,
        mouse_callbacks=screenshot_cb,
    )


def build_widgets(primary: bool = True) -> List[Any]:
    """Build the widget list for the primary or secondary screen."""
    theme = get_active_theme()
    visible_groups = [name for _, name in WORKSPACE_DEFS]

    # Right-clicking anywhere on the bar (unless overridden by a specific widget)
    # runs screenshot-and-gwenview.sh, matching `bindsym --release button3` in i3bar.simple.conf
    screenshot_script = str(BIN_DIR / "screenshot-and-gwenview.sh")
    bar_right_click = {
        "Button3": lambda: qtile.cmd_spawn(screenshot_script),
    }

    uname_info = platform.uname()
    uname_text = f"{uname_info.node}  {uname_info.release}"

    widgets: List[Any] = [
        # Workspaces (GroupBox)
        widget.GroupBox(
            font=FONT_FAMILY,
            fontsize=BAR_FONT_SIZE,
            visible_groups=visible_groups,
            margin_y=3,
            margin_x=0,
            padding_y=4,
            padding_x=6,
            borderwidth=2,
             active=theme["watxt"],
            inactive=theme["witxt"],
            rounded=False,
            highlight_method="block",
            this_current_screen_border=theme["wfbg"],
            this_screen_border=theme["wabg"],
            other_current_screen_border=theme["wfbg"],
            other_screen_border=theme["wabg"],
            block_highlight_text_color=theme["wftxt"],
            urgent_alert_method="block",
            urgent_border=theme["wubg"],
            urgent_text=theme["wutxt"],
            background=theme["background"],
            disable_drag=True,
            use_mouse_wheel=False,  # Matches `bindsym button4 nop` / `button5 nop`
            mouse_callbacks=bar_right_click,
        ),
        # Active KeyChord / Mode indicator (`binding_mode` in i3bar)
        widget.Chord(
            font=FONT_FAMILY,
            fontsize=BAR_FONT_SIZE,
            background=theme["bmbg"],
            foreground=theme["bmtxt"],
            padding=8,
        ),
        _sep(theme, bar_right_click),
        # Window tabs for the current workspace (emulates i3's tabbed title bars with icons)
        widget.TaskList(
            font=FONT_FAMILY,
            fontsize=BAR_FONT_SIZE - 1,
            background=theme["background"],
            foreground=theme["cftxt"],
            border=theme["cfbg"],
            unfocused_border=theme["cubg"],
            urgent_border=theme["curbg"],
            highlight_method="block",
            markup_focused="<span foreground='{fg}'>{text}</span>".format(
                fg=theme["cftxt"], text="{}"
            ),
            markup_normal="<span foreground='{fg}'>{text}</span>".format(
                fg=theme["cutxt"], text="{}"
            ),
            icon_size=0,  # Uses FontAwesome glyphs from format_window_title
            parse_text=lambda text: _format_tasklist_title(text),
            padding_x=8,
            padding_y=3,
            margin_x=2,
            margin_y=2,
            rounded=False,
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click),
        # 1. sysdata (CPU, Temp, RAM)
        widget.GenPollText(
            func=_poll_sysdata,
            update_interval=2,
            foreground=theme["status_good"],
            background=theme["background"],
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("xfce4-terminal -T GLANCES -e 'glances'"),
                "Button3": lambda: qtile.cmd_spawn("xfce4-terminal -T HTOP -e 'htop'"),
            },
        ),
        _sep(theme, bar_right_click),
        # 2. wifi
        widget.GenPollText(
            func=_poll_wifi,
            update_interval=5,
            foreground=theme["status_good"],
            background=theme["background"],
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("networkmanager_dmenu"),
                "Button3": lambda: qtile.cmd_spawn(screenshot_script),
            },
        ),
        _sep(theme, bar_right_click),
        # 3. uname ({node}  {release})
        widget.TextBox(
            text=uname_text,
            foreground=theme["status_color"],
            background=theme["background"],
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click),
        # 4. diskdata
        widget.GenPollText(
            func=_poll_diskdata,
            update_interval=30,
            foreground=theme["status_color"],
            background=theme["background"],
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click),
        # 5. online_status
        widget.GenPollText(
            func=_poll_online_status,
            update_interval=5,
            foreground=theme["status_good"],
            background=theme["background"],
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn("xfce4-terminal -e 'nmtui-connect'"),
                "Button3": lambda: qtile.cmd_spawn("xfce4-terminal -e 'nmtui-edit'"),
            },
        ),
        _sep(theme, bar_right_click),
        # 6. volume_status
        widget.GenPollText(
            func=_poll_volume,
            update_interval=1,
            foreground=theme["status_color"],
            background=theme["background"],
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
        _sep(theme, bar_right_click),
        # 7. battery_level
        widget.GenPollText(
            func=_poll_battery,
            update_interval=5,
            foreground=theme["status_good"],
            background=theme["background"],
            mouse_callbacks=bar_right_click,
        ),
        _sep(theme, bar_right_click),
        # 8. tztime local
        widget.Clock(
            format=" %a %d.%m  %H:%M",
            foreground=theme["status_color"],
            background=theme["background"],
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
                _sep(theme, bar_right_click),
                widget.Systray(
                    background=theme["background"],
                    padding=1,
                ),
            ]
        )

    return widgets


def build_screens() -> List[Screen]:
    """Build Screen configurations for all connected monitors (`id all-monitors`)."""
    theme = get_active_theme()
    position = get_bar_position()  # 'bottom' or 'top'

    primary_bar = bar.Bar(
        build_widgets(primary=True),
        size=28,
        background=theme["background"],
    )
    secondary_bar = bar.Bar(
        build_widgets(primary=False),
        size=28,
        background=theme["background"],
    )

    return [
        Screen(**{position: primary_bar}),
        Screen(**{position: secondary_bar}),
    ]
