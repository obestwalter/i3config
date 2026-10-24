"""Solarized color palette and Dark/Light themes.

Converted from:
- config.d/0-basic-setup.conf
- config.d/colors.0-dark.conf
- config.d/colors.1-light.conf
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

ThemeName = Literal["dark", "light"]

# Solarized base palette
BASE03: Final[str] = "#002b36"
BASE02: Final[str] = "#073642"
BASE01: Final[str] = "#586e75"
BASE00: Final[str] = "#657b83"
BASE0: Final[str] = "#839496"
BASE1: Final[str] = "#93a1a1"
BASE2: Final[str] = "#eee8d5"
BASE3: Final[str] = "#fdf6e3"

YELLOW: Final[str] = "#b58900"
ORANGE: Final[str] = "#cb4b16"
RED: Final[str] = "#dc322f"
MAGENTA: Final[str] = "#d33682"
VIOLET: Final[str] = "#6c71c4"
BLUE: Final[str] = "#268bd2"
CYAN: Final[str] = "#2aa198"
GREEN: Final[str] = "#859900"
WHITE: Final[str] = "#FFFFFF"
BLACK: Final[str] = "#000000"

LOCK_COLOR: Final[str] = ORANGE


@dataclass(frozen=True, slots=True)
class ColorTheme:
    """Immutable color scheme mapping i3wm client, workspace, bar, and status colors."""

    name: ThemeName
    accent: str

    # Client borders & backgrounds (focused, unfocused, focused_inactive, urgent)
    cfbr: str
    cfbg: str
    cftxt: str
    cfind: str
    cfchildb: str

    cubr: str
    cubg: str
    cutxt: str
    cuind: str
    cuchildb: str

    cfibr: str
    cfibg: str
    cfitxt: str
    cfiind: str
    cfichildb: str

    curbr: str
    curbg: str
    curtxt: str
    curind: str
    curchildb: str

    # Workspaces / GroupBox (focused, inactive, active, urgent)
    wfbr: str
    wfbg: str
    wftxt: str

    wibr: str
    wibg: str
    witxt: str

    wabr: str
    wabg: str
    watxt: str

    wubr: str
    wubg: str
    wutxt: str

    # Binding mode (KeyChord)
    bmbr: str
    bmbg: str
    bmtxt: str

    # Bar
    focused_background: str
    focused_statusline: str
    focused_separator: str
    background: str
    statusline: str
    separator: str

    # Status widgets (py3status equivalents)
    status_color: str
    status_good: str
    status_degraded: str
    status_bad: str

    def __getitem__(self, key: str) -> str:
        """Allow dict-style lookup (`theme['cfbg']`) as well as attribute access (`theme.cfbg`)."""
        return getattr(self, key)


# Dark Theme (colors.0-dark.conf)
DARK_THEME: Final[ColorTheme] = ColorTheme(
    name="dark",
    accent=BLUE,
    # Client
    cfbr=BASE3,
    cfbg=BLUE,
    cftxt=BASE3,
    cfind=BLUE,
    cfchildb=BASE3,
    cubr=BASE2,
    cubg=BASE02,
    cutxt=BASE1,
    cuind=BLUE,
    cuchildb=BASE3,
    cfibr=BASE2,
    cfibg=BASE03,
    cfitxt=BLUE,
    cfiind=BLUE,
    cfichildb=BASE03,
    curbr=BASE3,
    curbg=ORANGE,
    curtxt=BASE3,
    curind=BLUE,
    curchildb=CYAN,
    # Workspaces
    wfbr=BLUE,
    wfbg=BLUE,
    wftxt=BASE3,
    wibr=BASE02,
    wibg=BASE02,
    witxt=BASE1,
    wabr=BLUE,
    wabg=BASE02,
    watxt=BLUE,
    wubr=BASE3,
    wubg=ORANGE,
    wutxt=BASE3,
    # Binding mode
    bmbr=BASE3,
    bmbg=ORANGE,
    bmtxt=BASE3,
    # Bar
    focused_background=BASE2,
    focused_statusline=BLUE,
    focused_separator=BASE1,
    background=BASE03,
    statusline=RED,
    separator=BASE03,
    # Status
    status_color=BASE00,
    status_good=GREEN,
    status_degraded=VIOLET,
    status_bad=ORANGE,
)

# Light Theme (colors.1-light.conf)
LIGHT_THEME: Final[ColorTheme] = ColorTheme(
    name="light",
    accent=GREEN,
    # Client
    cfbr=BASE02,
    cfbg=GREEN,
    cftxt=BASE2,
    cfind=GREEN,
    cfchildb=BASE3,
    cubr=BASE02,
    cubg=BASE2,
    cutxt=BASE1,
    cuind=GREEN,
    cuchildb=BASE3,
    cfibr=BASE02,
    cfibg=BASE03,
    cfitxt=GREEN,
    cfiind=GREEN,
    cfichildb=BASE03,
    curbr=BASE3,
    curbg=CYAN,
    curtxt=BASE00,
    curind=GREEN,
    curchildb=CYAN,
    # Workspaces
    wfbr=BASE03,
    wfbg=GREEN,
    wftxt=BASE03,
    wibr=BASE02,
    wibg=BASE2,
    witxt=BASE1,
    wabr=BASE3,
    wabg=BASE03,
    watxt=GREEN,
    wubr=BASE3,
    wubg=ORANGE,
    wutxt=BASE3,
    # Binding mode
    bmbr=BASE03,
    bmbg=ORANGE,
    bmtxt=BASE3,
    # Bar
    focused_background=BASE3,
    focused_statusline=GREEN,
    focused_separator=BASE1,
    background=BASE02,
    statusline=RED,
    separator=BASE03,
    # Status
    status_color=BASE00,
    status_good=GREEN,
    status_degraded=VIOLET,
    status_bad=ORANGE,
)

THEMES: Final[tuple[ThemeName, ...]] = ("dark", "light")
THEME_MAP: Final[dict[ThemeName, ColorTheme]] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}
