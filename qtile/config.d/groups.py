"""Workspaces (Groups), ScratchPad, Sticky windows, and Window rules.

Converted from:
- config.d/0-basic-setup.conf (Workspaces $ws1..$ws10)
- config.d/3-window-settings.conf (Title icons, Zoom/PyCharm/FreeRDP/xfdesktop rules)
- config.d/control-main-key-bindings.conf (Scratchpad & sticky window bindings)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Final

from libqtile import hook
from libqtile.config import DropDown, Group, Match, ScratchPad
from libqtile.lazy import lazy

from settings import TERMINAL


@dataclass(frozen=True, slots=True)
class WorkspaceSpec:
    """Specification for a numbered i3-style workspace group."""

    key: str
    name: str
    layout: str = "max"


# Workspaces matching i3 $ws1 .. $ws10
WORKSPACE_SPECS: Final[tuple[WorkspaceSpec, ...]] = (
    WorkspaceSpec("1", " 1:   "),
    WorkspaceSpec("2", " 2: |  "),
    WorkspaceSpec("3", " 3:   "),
    WorkspaceSpec("4", " 4: |  "),
    WorkspaceSpec("5", " 5:   "),
    WorkspaceSpec("6", " 6:   "),
    WorkspaceSpec("7", " 7:   "),
    # 8 -> remote connections
    WorkspaceSpec("8", " 8:   "),
    # 9 -> admin / monitoring / logs
    WorkspaceSpec("9", " 9:  "),
    # 10 -> browser / secondary
    WorkspaceSpec("0", "10:  "),
)

# Backwards-compatible tuple list `(key_name, group_name)`
WORKSPACE_DEFS: Final[list[tuple[str, str]]] = [
    (spec.key, spec.name) for spec in WORKSPACE_SPECS
]

# Hidden group used to emulate i3's arbitrary window `move scratchpad` / `scratchpad show`
DYNAMIC_SCRATCHPAD_GROUP: Final[str] = "_i3_scratchpad"


def build_groups() -> list[Group]:
    """Create the 10 workspace groups plus Qtile ScratchPad."""
    groups: list[Group] = [
        # Default layout is "max" (tabbed equivalent when paired with bar TaskList)
        Group(name=spec.name, label=spec.name, layout=spec.layout)
        for spec in WORKSPACE_SPECS
    ]

    # Hidden group for moving arbitrary windows to/from the scratchpad (Shift+F12 / F12)
    groups.append(
        Group(name=DYNAMIC_SCRATCHPAD_GROUP, label="", init=True, persist=True)
    )

    # DropDown terminal scratchpad (cheap Yakuake emulation)
    groups.append(
        ScratchPad(
            "scratchpad",
            [
                DropDown(
                    "term",
                    f"{TERMINAL} --hide-menubar",
                    x=0.05,
                    y=0.05,
                    width=0.90,
                    height=0.85,
                    opacity=0.95,
                    on_focus_lost_hide=False,
                ),
            ],
        )
    )
    return groups


# ---------------------------------------------------------------------------
# Stateful Window Tracker (Scratchpad & Sticky Windows)
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class WindowStateTracker:
    """Tracks arbitrary scratchpad windows and sticky windows across workspaces."""

    scratchpad_windows: list[int] = field(default_factory=list)
    sticky_windows: set[int] = field(default_factory=set)

    def move_to_scratchpad(self, qtile_instance: Any) -> None:
        """Move the focused window to the hidden scratchpad (i3 `move scratchpad`)."""
        win = qtile_instance.current_window
        if win is None:
            return
        if win.wid not in self.scratchpad_windows:
            self.scratchpad_windows.append(win.wid)
        win.togroup(DYNAMIC_SCRATCHPAD_GROUP)

    def toggle_scratchpad(self, qtile_instance: Any) -> None:
        """Show/hide a window from the dynamic scratchpad, or toggle DropDown terminal."""
        win = qtile_instance.current_window
        if win is not None and win.wid in self.scratchpad_windows:
            win.togroup(DYNAMIC_SCRATCHPAD_GROUP)
            return

        scratch_group = qtile_instance.groups_map.get(DYNAMIC_SCRATCHPAD_GROUP)
        if scratch_group and scratch_group.windows:
            target = scratch_group.windows[-1]
            target.togroup(qtile_instance.current_group.name)
            target.enable_floating()
            target.bring_to_front()
            target.focus(warp=False)
            return

        scratchpad = qtile_instance.groups_map.get("scratchpad")
        if scratchpad and "term" in scratchpad.dropdowns:
            scratchpad.dropdowns["term"].toggle()

    def toggle_sticky(self, qtile_instance: Any) -> None:
        """Toggle whether the current window follows across all workspaces."""
        win = qtile_instance.current_window
        if win is None:
            return
        if win.wid in self.sticky_windows:
            self.sticky_windows.remove(win.wid)
        else:
            self.sticky_windows.add(win.wid)

    def sync_sticky_to_current_group(self, qtile_instance: Any) -> None:
        """Move all tracked sticky windows to the active workspace group."""
        if qtile_instance is None or not self.sticky_windows:
            return
        current_group = qtile_instance.current_group
        if current_group is None or current_group.name in (
            "scratchpad",
            DYNAMIC_SCRATCHPAD_GROUP,
        ):
            return
        for wid in list(self.sticky_windows):
            win = qtile_instance.windows_map.get(wid)
            if win is None:
                self.sticky_windows.discard(wid)
            elif win.group != current_group:
                win.togroup(current_group.name)

    def remove_window(self, wid: int) -> None:
        """Remove a closed window from tracking sets."""
        self.sticky_windows.discard(wid)
        if wid in self.scratchpad_windows:
            self.scratchpad_windows.remove(wid)


# Preserve the existing tracker instance across `importlib.reload(groups)` calls
TRACKER: WindowStateTracker = globals().get("TRACKER") or WindowStateTracker()


@lazy.function
def move_to_scratchpad(qtile_instance: Any) -> None:
    """Lazy command: move focused window to scratchpad."""
    TRACKER.move_to_scratchpad(qtile_instance)


@lazy.function
def toggle_scratchpad(qtile_instance: Any) -> None:
    """Lazy command: toggle scratchpad window or dropdown terminal."""
    TRACKER.toggle_scratchpad(qtile_instance)


@lazy.function
def toggle_sticky(qtile_instance: Any) -> None:
    """Lazy command: toggle sticky state on focused window."""
    TRACKER.toggle_sticky(qtile_instance)


@hook.subscribe.setgroup
def _move_sticky_windows() -> None:
    """Move all sticky windows to the newly focused group."""
    from libqtile import qtile

    TRACKER.sync_sticky_to_current_group(qtile)


@hook.subscribe.client_killed
def _cleanup_window_tracking(window: Any) -> None:
    """Remove closed windows from sticky and scratchpad tracking."""
    TRACKER.remove_window(window.wid)


# ---------------------------------------------------------------------------
# Window Title Icon Formatting & Floating Rules (3-window-settings.conf)
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class TitleIconRule:
    """Maps a regex pattern to a FontAwesome window title icon."""

    pattern: re.Pattern[str]
    icon: str

    def apply(self, title: str) -> str:
        prefix = f" {self.icon}  "
        return title if title.startswith(prefix) else f"{prefix}{title}"


ICON_CLASS_RULES: Final[tuple[TitleIconRule, ...]] = (
    TitleIconRule(re.compile(r"^Code$"), ""),
    TitleIconRule(re.compile(r"^Google-chrome$"), ""),
    TitleIconRule(re.compile(r"(?i)firefox"), ""),
    TitleIconRule(re.compile(r"^gwenview$"), ""),
    TitleIconRule(re.compile(r"^krusader$"), ""),
    TitleIconRule(re.compile(r"^jetbrains-pycharm$"), ""),
    TitleIconRule(re.compile(r"^Slack$"), ""),
    TitleIconRule(re.compile(r"^Thunderbird$"), ""),
    TitleIconRule(re.compile(r".*terminal.*"), ""),
    TitleIconRule(re.compile(r"^teams-for-linux$"), ""),
)

ICON_TITLE_RULES: Final[tuple[TitleIconRule, ...]] = (
    TitleIconRule(re.compile(r"^Write:.* Thunderbird"), ""),
    TitleIconRule(re.compile(r"^Volume Control$"), ""),
)

# Rules where i3 specifies `floating disable`
FORCE_TILE_MATCHES: Final[tuple[Match, ...]] = (
    Match(wm_class="zoom", wm_instance_class="zoom"),
    Match(wm_class="xfreerdp"),
    Match(title=re.compile(r"^FreeRDP:.*")),
)


def format_window_title(window: Any, text: str) -> str:
    """Format window title with FontAwesome application icons from 3-window-settings.conf."""
    if window is None:
        return text

    # Check title-specific rules first (e.g. "Write:.* Thunderbird" overrides class "Thunderbird")
    for rule in ICON_TITLE_RULES:
        if rule.pattern.search(text):
            return rule.apply(text)

    # Check WM_CLASS rules
    wm_classes = window.get_wm_class() or []
    for wm_cls in wm_classes:
        for rule in ICON_CLASS_RULES:
            if rule.pattern.search(wm_cls):
                return rule.apply(text)

    return text


@hook.subscribe.client_new
def _apply_window_rules(window: Any) -> None:
    """Apply `floating disable` rules from 3-window-settings.conf."""
    for match in FORCE_TILE_MATCHES:
        if match.compare(window):
            window.floating = False
            break
