"""Solarized color palette and Dark/Light themes.

Converted from:
- config.d/0-basic-setup.conf
- config.d/colors.0-dark.conf
- config.d/colors.1-light.conf
"""

from typing import Dict

# Solarized base palette
BASE03 = "#002b36"
BASE02 = "#073642"
BASE01 = "#586e75"
BASE00 = "#657b83"
BASE0 = "#839496"
BASE1 = "#93a1a1"
BASE2 = "#eee8d5"
BASE3 = "#fdf6e3"

YELLOW = "#b58900"
ORANGE = "#cb4b16"
RED = "#dc322f"
MAGENTA = "#d33682"
VIOLET = "#6c71c4"
BLUE = "#268bd2"
CYAN = "#2aa198"
GREEN = "#859900"
WHITE = "#FFFFFF"
BLACK = "#000000"

LOCK_COLOR = ORANGE

# Dark Theme (colors.0-dark.conf)
DARK_THEME: Dict[str, str] = {
    "name": "dark",
    "accent": BLUE,
    # Client borders & backgrounds
    "cfbr": BASE3,
    "cfbg": BLUE,
    "cftxt": BASE3,
    "cfind": BLUE,
    "cfchildb": BASE3,
    "cubr": BASE2,
    "cubg": BASE02,
    "cutxt": BASE1,
    "cuind": BLUE,
    "cuchildb": BASE3,
    "cfibr": BASE2,
    "cfibg": BASE03,
    "cfitxt": BLUE,
    "cfiind": BLUE,
    "cfichildb": BASE03,
    "curbr": BASE3,
    "curbg": ORANGE,
    "curtxt": BASE3,
    "curind": BLUE,
    "curchildb": CYAN,
    # Workspaces (GroupBox)
    "wfbr": BLUE,
    "wfbg": BLUE,
    "wftxt": BASE3,
    "wibr": BASE02,
    "wibg": BASE02,
    "witxt": BASE1,
    "wabr": BLUE,
    "wabg": BASE02,
    "watxt": BLUE,
    "wubr": BASE3,
    "wubg": ORANGE,
    "wutxt": BASE3,
    # Binding mode (KeyChord)
    "bmbr": BASE3,
    "bmbg": ORANGE,
    "bmtxt": BASE3,
    # Bar
    "focused_background": BASE2,
    "focused_statusline": BLUE,
    "focused_separator": BASE1,
    "background": BASE03,
    "statusline": RED,
    "separator": BASE03,
    # Status widgets (py3status equivalents)
    "status_color": BASE00,
    "status_good": GREEN,
    "status_degraded": VIOLET,
    "status_bad": ORANGE,
}

# Light Theme (colors.1-light.conf)
LIGHT_THEME: Dict[str, str] = {
    "name": "light",
    "accent": GREEN,
    # Client borders & backgrounds
    "cfbr": BASE02,
    "cfbg": GREEN,
    "cftxt": BASE2,
    "cfind": GREEN,
    "cfchildb": BASE3,
    "cubr": BASE02,
    "cubg": BASE2,
    "cutxt": BASE1,
    "cuind": GREEN,
    "cuchildb": BASE3,
    "cfibr": BASE02,
    "cfibg": BASE03,
    "cfitxt": GREEN,
    "cfiind": GREEN,
    "cfichildb": BASE03,
    "curbr": BASE3,
    "curbg": CYAN,
    "curtxt": BASE00,
    "curind": GREEN,
    "curchildb": CYAN,
    # Workspaces (GroupBox)
    "wfbr": BASE03,
    "wfbg": GREEN,
    "wftxt": BASE03,
    "wibr": BASE02,
    "wibg": BASE2,
    "witxt": BASE1,
    "wabr": BASE3,
    "wabg": BASE03,
    "watxt": GREEN,
    "wubr": BASE3,
    "wubg": ORANGE,
    "wutxt": BASE3,
    # Binding mode (KeyChord)
    "bmbr": BASE03,
    "bmbg": ORANGE,
    "bmtxt": BASE3,
    # Bar
    "focused_background": BASE3,
    "focused_statusline": GREEN,
    "focused_separator": BASE1,
    "background": BASE02,
    "statusline": RED,
    "separator": BASE03,
    # Status widgets (py3status equivalents)
    "status_color": BASE00,
    "status_good": GREEN,
    "status_degraded": VIOLET,
    "status_bad": ORANGE,
}

THEMES = ["dark", "light"]
THEME_MAP = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}
