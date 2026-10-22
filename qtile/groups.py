"""Workspaces (Groups), ScratchPad, Sticky windows, and Window rules.

Converted from:
- config.d/0-basic-setup.conf (Workspaces $ws1..$ws10)
- config.d/3-window-settings.conf (Title icons, Zoom/PyCharm/FreeRDP/xfdesktop rules)
- config.d/control-main-key-bindings.conf (Scratchpad & sticky window bindings)
"""

import re
from typing import List, Tuple
from libqtile import hook
from libqtile.config import DropDown, Group, Match, ScratchPad
from libqtile.lazy import lazy

from settings import TERMINAL

# Workspaces matching i3 $ws1 .. $ws10
# Tuple format: (key_name, group_name_and_label)
WORKSPACE_DEFS: List[Tuple[str, str]] = [
    ("1", " 1:   "),
    ("2", " 2: |  "),
    ("3", " 3:   "),
    ("4", " 4: |  "),
    ("5", " 5:   "),
    ("6", " 6:   "),
    ("7", " 7:   "),
    # 8 -> remote connections
    ("8", " 8:   "),
    # 9 -> admin / monitoring / logs
    ("9", " 9:  "),
    # 10 -> browser / secondary
    ("0", "10:  "),
]

# Hidden group used to emulate i3's arbitrary window `move scratchpad` / `scratchpad show`
DYNAMIC_SCRATCHPAD_GROUP = "_i3_scratchpad"


def build_groups() -> List[Group]:
    """Create the 10 workspace groups plus Qtile ScratchPad."""
    groups: List[Group] = [
        # Default layout is "max" (tabbed equivalent when paired with bar WindowTabs/TaskList)
        Group(name=ws_name, label=ws_name, layout="max")
        for _, ws_name in WORKSPACE_DEFS
    ]

    # Hidden group for moving arbitrary windows to/from the scratchpad (Shift+F12 / F12)
    groups.append(Group(name=DYNAMIC_SCRATCHPAD_GROUP, label="", init=True, persist=True))

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
# Arbitrary Window Scratchpad (i3 `move scratchpad` / `scratchpad show`)
# ---------------------------------------------------------------------------
_scratchpad_windows: List[int] = []


@lazy.function
def move_to_scratchpad(qtile) -> None:
    """Move the focused window to the hidden scratchpad (i3 `move scratchpad`)."""
    win = qtile.current_window
    if win is None:
        return
    if win.wid not in _scratchpad_windows:
        _scratchpad_windows.append(win.wid)
    win.togroup(DYNAMIC_SCRATCHPAD_GROUP)


@lazy.function
def toggle_scratchpad(qtile) -> None:
    """Show/hide the window in the dynamic scratchpad, or toggle DropDown terminal."""
    win = qtile.current_window
    # If the currently focused window came from the dynamic scratchpad, hide it back
    if win is not None and win.wid in _scratchpad_windows:
        win.togroup(DYNAMIC_SCRATCHPAD_GROUP)
        return

    # Otherwise, check if the hidden scratchpad group has any windows
    scratch_group = qtile.groups_map.get(DYNAMIC_SCRATCHPAD_GROUP)
    if scratch_group and scratch_group.windows:
        target = scratch_group.windows[-1]
        target.togroup(qtile.current_group.name)
        target.enable_floating()
        target.bring_to_front()
        target.focus(warp=False)
        return

    # Fallback: toggle the ScratchPad DropDown terminal
    scratchpad = qtile.groups_map.get("scratchpad")
    if scratchpad and "term" in scratchpad.dropdowns:
        scratchpad.dropdowns["term"].toggle()


# ---------------------------------------------------------------------------
# Sticky Windows (i3 `sticky toggle` on Control+F12)
# ---------------------------------------------------------------------------
_sticky_windows: set[int] = set()


@lazy.function
def toggle_sticky(qtile) -> None:
    """Toggle whether the current window follows across all workspaces."""
    win = qtile.current_window
    if win is None:
        return
    if win.wid in _sticky_windows:
        _sticky_windows.remove(win.wid)
    else:
        _sticky_windows.add(win.wid)


@hook.subscribe.setgroup
def _move_sticky_windows() -> None:
    """Move all sticky windows to the newly focused group."""
    from libqtile import qtile

    if qtile is None or not _sticky_windows:
        return
    current_group = qtile.current_group
    if current_group is None or current_group.name in ("scratchpad", DYNAMIC_SCRATCHPAD_GROUP):
        return
    for wid in list(_sticky_windows):
        win = qtile.windows_map.get(wid)
        if win is None:
            _sticky_windows.discard(wid)
        elif win.group != current_group:
            win.togroup(current_group.name)


@hook.subscribe.client_killed
def _cleanup_window_tracking(window) -> None:
    """Remove closed windows from sticky and scratchpad tracking."""
    _sticky_windows.discard(window.wid)
    if window.wid in _scratchpad_windows:
        _scratchpad_windows.remove(window.wid)


# ---------------------------------------------------------------------------
# Window Title Icon Formatting & Floating Rules (3-window-settings.conf)
# ---------------------------------------------------------------------------
# Rules matching i3 `for_window [...] title_format " <icon>  %title"`
ICON_CLASS_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^Code$"), ""),
    (re.compile(r"^Google-chrome$"), ""),
    (re.compile(r"(?i)firefox"), ""),
    (re.compile(r"^gwenview$"), ""),
    (re.compile(r"^krusader$"), ""),
    (re.compile(r"^jetbrains-pycharm$"), ""),
    (re.compile(r"^Slack$"), ""),
    (re.compile(r"^Thunderbird$"), ""),
    (re.compile(r".*terminal.*"), ""),
    (re.compile(r"^teams-for-linux$"), ""),
]

ICON_TITLE_RULES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^Write:.* Thunderbird"), ""),
    (re.compile(r"^Volume Control$"), ""),
]

# Rules where i3 specifies `floating disable`
FORCE_TILE_MATCHES: List[Match] = [
    Match(wm_class="zoom", wm_instance_class="zoom"),
    Match(wm_class="xfreerdp"),
    Match(title=re.compile(r"^FreeRDP:.*")),
]


def format_window_title(window, text: str) -> str:
    """Format window title with FontAwesome application icons from 3-window-settings.conf."""
    if window is None:
        return text

    # Check title-specific rules first (e.g. "Write:.* Thunderbird" overrides class "Thunderbird")
    for pattern, icon in ICON_TITLE_RULES:
        if pattern.search(text):
            prefix = f" {icon}  "
            return text if text.startswith(prefix) else f"{prefix}{text}"

    # Check WM_CLASS rules
    wm_classes = window.get_wm_class() or []
    for wm_cls in wm_classes:
        for pattern, icon in ICON_CLASS_RULES:
            if pattern.search(wm_cls):
                prefix = f" {icon}  "
                return text if text.startswith(prefix) else f"{prefix}{text}"

    return text


@hook.subscribe.client_new
def _apply_window_rules(window) -> None:
    """Apply `floating disable` rules from 3-window-settings.conf."""
    for match in FORCE_TILE_MATCHES:
        if match.compare(window):
            window.floating = False
            break
