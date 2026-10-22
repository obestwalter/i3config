"""Keybindings, KeyChord modes, and mouse bindings.

Converted from:
- config.d/control-main-key-bindings.conf
- config.d/mode-central-control.conf
- config.d/mode-i3configger.conf
- config.d/mode-resize.conf
"""

import subprocess
from typing import List
from libqtile.config import Click, Drag, Key, KeyChord, Mouse
from libqtile.lazy import lazy

from groups import (
    DYNAMIC_SCRATCHPAD_GROUP,
    WORKSPACE_DEFS,
    move_to_scratchpad,
    toggle_scratchpad,
    toggle_sticky,
)
from settings import (
    ALT,
    BIN_DIR,
    CTRL,
    MOD,
    SHIFT,
    TERMINAL_MAXIMIZED,
    WALLPAPER_LOCK,
    cycle_theme,
    set_bar_position,
)


# ---------------------------------------------------------------------------
# Helper functions for i3-equivalent navigation & manipulation
# ---------------------------------------------------------------------------
@lazy.function
def focus_direction(qtile, direction: str) -> None:
    """Focus window in direction; in Max (tabbed) layout, Left/Up & Right/Down cycle tabs."""
    layout_name = qtile.current_layout.name
    if layout_name == "max":
        if direction in ("left", "up"):
            qtile.current_group.prev_window()
        else:
            qtile.current_group.next_window()
    else:
        getattr(qtile.current_layout, direction)()


@lazy.function
def step_visible_group(qtile, step: int) -> None:
    """Switch to previous/next workspace, skipping hidden scratchpad groups."""
    valid_names = [name for _, name in WORKSPACE_DEFS]
    current_name = qtile.current_group.name
    if current_name not in valid_names:
        qtile.groups_map[valid_names[0]].toscreen(toggle=False)
        return
    idx = (valid_names.index(current_name) + step) % len(valid_names)
    qtile.groups_map[valid_names[idx]].toscreen(toggle=False)


@lazy.function
def focus_mode_toggle(qtile) -> None:
    """Toggle focus between floating and tiled windows (`focus mode_toggle` in i3)."""
    group = qtile.current_group
    win = qtile.current_window
    if not group or not group.windows:
        return
    want_floating = not (win and win.floating)
    for candidate in group.windows:
        if candidate.floating == want_floating:
            group.focus(candidate, warp=True)
            if candidate.floating:
                candidate.bring_to_front()
            return


@lazy.function
def toggle_split_or_columns(qtile) -> None:
    """Switch to `columns` layout or toggle split mode (`layout toggle split` in i3)."""
    if qtile.current_layout.name != "columns":
        for idx, lyt in enumerate(qtile.current_group.layouts):
            if lyt.name == "columns":
                qtile.current_group.use_layout(idx)
                return
    else:
        qtile.current_layout.toggle_split()


@lazy.function
def move_workspace_to_next_screen(qtile) -> None:
    """Move the current workspace to the next monitor (`move workspace to output next` in i3)."""
    if len(qtile.screens) < 2:
        return
    current_group = qtile.current_group
    next_screen_idx = (qtile.current_screen.index + 1) % len(qtile.screens)
    current_group.toscreen(next_screen_idx)
    qtile.focus_screen(next_screen_idx)


@lazy.function
def switch_theme_and_reload(qtile, step: int) -> None:
    """Cycle dark/light Solarized theme, reload Qtile config, and send notification."""
    cycle_theme(step)
    qtile.reload_config()
    subprocess.Popen(["notify-send", "-a", "CENTRAL-CONTROL-PROGRAM", "Qtile theme switched"])


@lazy.function
def switch_bar_position_and_reload(qtile, position: str) -> None:
    """Move bar to top or bottom, reload Qtile config, and send notification."""
    set_bar_position(position)
    qtile.reload_config()
    subprocess.Popen(["notify-send", "-a", "CENTRAL-CONTROL-PROGRAM", f"Bar moved to {position}"])


@lazy.function
def resize_window(qtile, dw: int, dh: int) -> None:
    """Resize floating or tiled window by (dw, dh) pixels (`mode-resize.conf`)."""
    win = qtile.current_window
    if win is None:
        return
    if win.floating:
        win.resize_floating(dw, dh)
    else:
        layout = qtile.current_layout
        if dw < 0 and hasattr(layout, "grow_left"):
            layout.grow_left()
        elif dw > 0 and hasattr(layout, "grow_right"):
            layout.grow_right()
        if dh < 0 and hasattr(layout, "grow_up"):
            layout.grow_up()
        elif dh > 0 and hasattr(layout, "grow_down"):
            layout.grow_down()


@lazy.function
def move_window_by(qtile, dx: int, dy: int) -> None:
    """Move floating window by (dx, dy) pixels, or shuffle tiled window (`mode-resize.conf`)."""
    win = qtile.current_window
    if win is None:
        return
    if win.floating:
        win.move_floating(dx, dy)
    else:
        layout = qtile.current_layout
        if dx < 0 and hasattr(layout, "shuffle_left"):
            layout.shuffle_left()
        elif dx > 0 and hasattr(layout, "shuffle_right"):
            layout.shuffle_right()
        if dy < 0 and hasattr(layout, "shuffle_up"):
            layout.shuffle_up()
        elif dy > 0 and hasattr(layout, "shuffle_down"):
            layout.shuffle_down()


def build_keys() -> List[Key | KeyChord]:
    """Build all Qtile keybindings and modes."""
    keys: List[Key | KeyChord] = [
        # ===================================================================
        # Navigate (control-main-key-bindings.conf)
        # ===================================================================
        Key([ALT], "Tab", lazy.screen.toggle_group(), desc="Workspace back and forth"),
        Key([MOD], "Left", focus_direction("left"), desc="Focus left / prev tab"),
        Key([MOD], "Down", focus_direction("down"), desc="Focus down / next tab"),
        Key([MOD], "Up", focus_direction("up"), desc="Focus up / prev tab"),
        Key([MOD], "Right", focus_direction("right"), desc="Focus right / next tab"),
        Key([MOD, ALT], "Left", step_visible_group(-1), desc="Previous workspace"),
        Key([MOD, ALT], "Right", step_visible_group(1), desc="Next workspace"),
        # Mod4+e also switches to workspace 2 (" 2: |  ")
        Key([MOD], "e", lazy.group[" 2: |  "].toscreen(toggle=False), desc="Workspace 2"),

        # ===================================================================
        # Manipulate
        # ===================================================================
        Key([MOD, SHIFT], "numbersign", lazy.window.kill(), desc="Kill focused window"),
        Key([], "F11", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
        Key([CTRL], "F12", toggle_sticky(), desc="Toggle sticky window across workspaces"),

        Key([MOD], "asciicircum", focus_mode_toggle(), desc="Toggle focus floating/tiling"),
        Key([MOD], "u", lazy.group.setlayout("max"), desc="Layout tabbed (max)"),
        Key([MOD], "i", lazy.group.setlayout("stack"), desc="Layout stacking (stack)"),
        Key([MOD], "o", toggle_split_or_columns(), desc="Layout toggle split (columns)"),
        # win+ü - toggle between all layout types
        Key([MOD], "udiaeresis", lazy.next_layout(), desc="Toggle between all layout types"),

        # asciicircum == ° (roof sign + shift)
        Key([MOD, SHIFT], "asciicircum", lazy.window.toggle_floating(), desc="Toggle floating"),

        # Move workspace to next monitor
        Key([MOD], "x", move_workspace_to_next_screen(), desc="Move workspace to next monitor"),

        # Move window in current layout
        Key([MOD, SHIFT], "Left", lazy.layout.shuffle_left(), desc="Move window left"),
        Key([MOD, SHIFT], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
        Key([MOD, SHIFT], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
        Key([MOD, SHIFT], "Right", lazy.layout.shuffle_right(), desc="Move window right"),

        # ===================================================================
        # Terminal / Scratchpad (cheap Yakuake emulation)
        # ===================================================================
        Key([SHIFT], "F12", move_to_scratchpad(), desc="Move focused window to scratchpad"),
        Key([], "F12", toggle_scratchpad(), desc="Show/toggle scratchpad"),
        Key([MOD], "Return", toggle_scratchpad(), desc="Show/toggle scratchpad"),
        Key([MOD, SHIFT], "Return", lazy.spawn(TERMINAL_MAXIMIZED), desc="Launch maximized terminal"),

        # ===================================================================
        # Rofi
        # ===================================================================
        Key(
            [ALT],
            "space",
            lazy.spawn(
                f"rofi -combi-modi window,drun,run -show combi "
                f"-modi combi,run,files:{BIN_DIR}/rofi-file-browser.sh"
            ),
            desc="Rofi combi launcher & file browser",
        ),
        Key([MOD], "a", lazy.spawn("rofi -show window"), desc="Rofi window switcher"),
        Key(
            [MOD, SHIFT],
            "Tab",
            lazy.spawn(
                f"rofi -modi 'Workspace:{BIN_DIR}/rofi-qtile-ws-list.sh,"
                f"Move to Workspace:{BIN_DIR}/rofi-qtile-ws-move.sh' -show Workspace"
            ),
            desc="Rofi workspace switcher / mover",
        ),

        # ===================================================================
        # FN Keys / Special Controls
        # ===================================================================
        Key(
            [MOD],
            "F4",
            lazy.spawn("xbacklight e -ctrl intel_backlight -dec 5"),
            desc="Decrease brightness 5%",
        ),
        Key(
            [MOD],
            "F5",
            lazy.spawn("xbacklight e -ctrl intel_backlight -inc 5"),
            desc="Increase brightness 5%",
        ),
        Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause"), desc="Media play/pause"),
        Key([], "XF86AudioPause", lazy.spawn("playerctl play-pause"), desc="Media play/pause"),
        Key(
            [],
            "XF86AudioRaiseVolume",
            lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +2%"),
            desc="Raise volume +2%",
        ),
        Key(
            [],
            "XF86AudioLowerVolume",
            lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -2%"),
            desc="Lower volume -2%",
        ),
        Key(
            [],
            "XF86AudioMute",
            lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle"),
            desc="Toggle mute",
        ),
        Key([], "XF86AudioNext", lazy.spawn("playerctl next"), desc="Media next track"),
        Key([], "XF86AudioPrev", lazy.spawn("playerctl previous"), desc="Media previous track"),

        # Print key | Druck/S-Abfr
        Key([MOD], "F10", lazy.spawn("xfce4-screenshooter --region"), desc="Screenshot region"),
        Key(
            [MOD, SHIFT],
            "F10",
            lazy.spawn("xfce4-screenshooter --fullscreen"),
            desc="Screenshot fullscreen",
        ),

        # Misc
        Key([MOD], "y", lazy.spawn("xdotool key Menu"), desc="Context menu (Menu key)"),
        Key([MOD], "period", lazy.hide_show_bar(), desc="Toggle status bar visibility"),

        # ===================================================================
        # Mode 1: CENTRAL-CONTROL-PROGRAM (mode-central-control.conf)
        # Single-action chord (automatically exits to default mode after keypress)
        # ===================================================================
        KeyChord(
            [MOD],
            "c",
            [
                Key([], "g", lazy.spawn("scrot"), desc="Take screenshot with scrot"),
                Key(
                    [],
                    "k",
                    lazy.spawn(str(BIN_DIR / "toggle-screenkey.sh")),
                    desc="Toggle screenkey",
                ),
                Key(
                    [],
                    "l",
                    lazy.spawn(f"i3lock -f -t -i {WALLPAPER_LOCK}"),
                    desc="Lock screen with i3lock",
                ),
                Key(
                    [],
                    "s",
                    lazy.spawn(
                        ["sh", "-c", f"i3lock -f -t -i {WALLPAPER_LOCK} && systemctl suspend"]
                    ),
                    desc="Lock screen and suspend",
                ),
                Key(
                    [],
                    "t",
                    lazy.spawn(str(BIN_DIR / "toggle-touchpad.sh")),
                    desc="Toggle touchpad",
                ),
                Key(
                    [],
                    "u",
                    lazy.spawn(str(BIN_DIR / "toggle-unclutter.sh")),
                    desc="Toggle unclutter",
                ),
            ],
            mode=False,
            name="CENTRAL-CONTROL-PROGRAM   =>  g: scrot  k: screenkey  l: lock  s: suspend  t: touchpad  u: unclutter",
        ),

        # ===================================================================
        # Mode 2: Qtile Config & Theme Control (mode-i3configger.conf)
        # ===================================================================
        KeyChord(
            [MOD],
            "w",
            [
                Key([], "Return", lazy.reload_config(), desc="Reload Qtile config"),
                Key([], "Left", switch_theme_and_reload(-1), desc="Previous Solarized theme"),
                Key([], "Right", switch_theme_and_reload(1), desc="Next Solarized theme"),
                Key([], "Up", switch_bar_position_and_reload("top"), desc="Move bar to top"),
                Key(
                    [],
                    "Down",
                    switch_bar_position_and_reload("bottom"),
                    desc="Move bar to bottom",
                ),
                Key(
                    [],
                    "c",
                    lazy.restart(),
                    lazy.spawn(
                        ["notify-send", "-a", "CENTRAL-CONTROL-PROGRAM", "Qtile restarted"]
                    ),
                    desc="Restart Qtile",
                ),
                Key(
                    [],
                    "r",
                    lazy.reload_config(),
                    lazy.spawn(
                        ["notify-send", "-a", "CENTRAL-CONTROL-PROGRAM", "Qtile reloaded"]
                    ),
                    desc="Reload Qtile config",
                ),
                Key([], "x", lazy.shutdown(), desc="Exit Qtile"),
            ],
            mode=False,
            name="qtile-config  =>  Return: reload  Left/Right: prev/next colors  Up/Down: bar top/bottom  c: restart  r: reload  x: exit",
        ),

        # ===================================================================
        # Mode 3: Resize / Move (mode-resize.conf)
        # Persistent mode (mode=True) until Escape is pressed
        # ===================================================================
        KeyChord(
            [MOD],
            "r",
            [
                # Resize by 100 px
                Key([], "Left", resize_window(-100, 0), desc="Shrink width 100px"),
                Key([], "Down", resize_window(0, 100), desc="Grow height 100px"),
                Key([], "Up", resize_window(0, -100), desc="Shrink height 100px"),
                Key([], "Right", resize_window(100, 0), desc="Grow width 100px"),
                # Resize by 10 px
                Key([SHIFT], "Left", resize_window(-10, 0), desc="Shrink width 10px"),
                Key([SHIFT], "Down", resize_window(0, 10), desc="Grow height 10px"),
                Key([SHIFT], "Up", resize_window(0, -10), desc="Shrink height 10px"),
                Key([SHIFT], "Right", resize_window(10, 0), desc="Grow width 10px"),
                # Resize by 1 px
                Key([], "h", resize_window(-1, 0), desc="Shrink width 1px"),
                Key([], "j", resize_window(0, 1), desc="Grow height 1px"),
                Key([], "k", resize_window(0, -1), desc="Shrink height 1px"),
                Key([], "l", resize_window(1, 0), desc="Grow width 1px"),
                # Move by 100 px
                Key([CTRL], "Left", move_window_by(-100, 0), desc="Move left 100px"),
                Key([CTRL], "Right", move_window_by(100, 0), desc="Move right 100px"),
                Key([CTRL], "Up", move_window_by(0, -100), desc="Move up 100px"),
                Key([CTRL], "Down", move_window_by(0, 100), desc="Move down 100px"),
                # Move by 10 px
                Key([CTRL, SHIFT], "Left", move_window_by(-10, 0), desc="Move left 10px"),
                Key([CTRL, SHIFT], "Right", move_window_by(10, 0), desc="Move right 10px"),
                Key([CTRL, SHIFT], "Up", move_window_by(0, -10), desc="Move up 10px"),
                Key([CTRL, SHIFT], "Down", move_window_by(0, 10), desc="Move down 10px"),
                # Move by 1 px
                Key([CTRL], "h", move_window_by(-1, 0), desc="Move left 1px"),
                Key([CTRL], "j", move_window_by(0, 1), desc="Move down 1px"),
                Key([CTRL], "k", move_window_by(0, -1), desc="Move up 1px"),
                Key([CTRL], "l", move_window_by(1, 0), desc="Move right 1px"),
            ],
            mode=True,
            name="resize / move",
        ),
    ]

    # Workspace switching (Mod4 + 1..0) and moving container to workspace (Mod4 + Shift + 1..0)
    for key_name, ws_name in WORKSPACE_DEFS:
        keys.append(
            Key(
                [MOD],
                key_name,
                lazy.group[ws_name].toscreen(toggle=False),
                desc=f"Switch to workspace {ws_name.strip()}",
            )
        )
        keys.append(
            Key(
                [MOD, SHIFT],
                key_name,
                lazy.window.togroup(ws_name, switch_group=False),
                desc=f"Move window to workspace {ws_name.strip()}",
            )
        )

    return keys


def build_mouse() -> List[Mouse]:
    """Mouse bindings for floating windows (`floating_modifier Mod4`)."""
    return [
        Drag(
            [MOD],
            "Button1",
            lazy.window.set_position_floating(),
            start=lazy.window.get_position(),
        ),
        Drag(
            [MOD],
            "Button3",
            lazy.window.set_size_floating(),
            start=lazy.window.get_size(),
        ),
        Click([MOD], "Button2", lazy.window.bring_to_front()),
    ]
