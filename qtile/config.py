"""Main Qtile configuration entrypoint (~/.config/qtile/config.py).

Converted from i3wm configuration (`config` and `config.d/*`).

To install/activate:
    ln -sfn "$(pwd)/qtile" ~/.config/qtile
"""

import sys
from pathlib import Path

# Ensure sibling modules in `qtile/` are importable even if `config.py` is symlinked
_CONFIG_DIR = str(Path(__file__).resolve().parent)
if _CONFIG_DIR not in sys.path:
    sys.path.insert(0, _CONFIG_DIR)

# Import startup hooks so @hook.subscribe decorators are registered
import startup  # noqa: F401
from bar import build_screens
from groups import build_groups
from keys import build_keys, build_mouse
from layouts import build_floating_layout, build_layouts
from settings import FONT_FAMILY, get_active_theme, get_bar_font_size

# ---------------------------------------------------------------------------
# Keybindings, Mouse, Groups, Layouts, and Screens
# ---------------------------------------------------------------------------
keys = build_keys()
mouse = build_mouse()
groups = build_groups()
layouts = build_layouts()
floating_layout = build_floating_layout()
screens = build_screens()

# Default widget settings (`i3bar.simple.conf`: font pango:DejaVu Sans Mono 15, FontAwesome 15)
_theme = get_active_theme()
widget_defaults = {
    "font": FONT_FAMILY,
    "fontsize": get_bar_font_size(),
    "padding": 4,
    "background": _theme["background"],
    "foreground": _theme["status_color"],
}
extension_defaults = widget_defaults.copy()

# ---------------------------------------------------------------------------
# General Qtile Behavior Settings (from `0-basic-setup.conf`)
# ---------------------------------------------------------------------------
dgroups_key_binder = None
dgroups_app_rules = []  # type: list

# focus_follows_mouse no
follow_mouse_focus = False

# Bring floating window to front when clicked
bring_front_click = False
floats_kept_above = True

# mouse_warping output
cursor_warp = True

# popup_during_fullscreen smart
auto_fullscreen = True

# focus_on_window_activation smart
focus_on_window_activation = "smart"

reconfigure_screens = True
auto_minimize = True
wl_input_rules = None

# Pretend to be LG3D so Java/Swing applications (like JetBrains PyCharm) render properly
wmname = "LG3D"
