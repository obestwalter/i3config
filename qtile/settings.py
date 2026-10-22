"""Basic variables, paths, and persistent runtime state (theme & bar position).

Converted from:
- config.d/0-basic-setup.conf
- config.d/i3configger.json
"""

import json
from pathlib import Path
from typing import Any, Dict

from colors import DARK_THEME, THEME_MAP, THEMES

# Paths (resolved relative to this repository or ~/.i3 fallback)
REPO_ROOT = Path(__file__).resolve().parent.parent
I3_HOME = REPO_ROOT if (REPO_ROOT / "bin").is_dir() else Path.home() / ".i3"
BIN_DIR = I3_HOME / "bin"
CONFIGS_OTHER_DIR = I3_HOME / "configs-other"
WALLPAPER_LOCK = Path.home() / "Pictures/wallpapers/single_screen/generative-orange.png"

# Runtime state file (replaces i3configger state for theme & bar position)
STATE_FILE = Path.home() / ".config" / "qtile" / "state.json"

# Modifiers
MOD = "mod4"
ALT = "mod1"
CTRL = "control"
SHIFT = "shift"

# Fonts (from 0-basic-setup.conf & i3bar.simple.conf)
FONT_FAMILY = "DejaVu Sans Mono"
FONT_SIZE = 14
BAR_FONT_SIZE = 15
BAR_SEPARATOR = " ║ "

# Applications
TERMINAL = "xfce4-terminal"
TERMINAL_MAXIMIZED = "xfce4-terminal --maximize --hide-menubar"


def load_state() -> Dict[str, Any]:
    """Load persisted theme and bar position state."""
    default_state = {
        "theme": "dark",
        "bar_position": "bottom",
    }
    try:
        if STATE_FILE.is_file():
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                default_state.update(data)
    except Exception:
        pass
    return default_state


def save_state(state: Dict[str, Any]) -> None:
    """Persist theme and bar position state to disk."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_active_theme() -> Dict[str, str]:
    """Return the active color theme dictionary."""
    state = load_state()
    theme_name = state.get("theme", "dark")
    return THEME_MAP.get(theme_name, DARK_THEME)


def get_bar_position() -> str:
    """Return 'top' or 'bottom' for the status bar."""
    state = load_state()
    pos = state.get("bar_position", "bottom")
    return pos if pos in ("top", "bottom") else "bottom"


def cycle_theme(step: int = 1) -> None:
    """Switch to the next/previous color theme and save state."""
    state = load_state()
    current = state.get("theme", "dark")
    idx = THEMES.index(current) if current in THEMES else 0
    new_theme = THEMES[(idx + step) % len(THEMES)]
    state["theme"] = new_theme
    save_state(state)


def set_bar_position(position: str) -> None:
    """Set bar position ('top' or 'bottom') and save state."""
    if position in ("top", "bottom"):
        state = load_state()
        state["bar_position"] = position
        save_state(state)
