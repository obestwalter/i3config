"""Basic variables, paths, process helpers, and persistent runtime state.

Converted from:
- config.d/0-basic-setup.conf
- config.d/i3configger.json
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, Literal

from colors import DARK_THEME, THEME_MAP, THEMES, ColorTheme, ThemeName

BarPosition = Literal["top", "bottom"]

# Paths (resolved relative to the qtile folder, ~/.config/qtile fallback).
# Layout mirrors the i3 setup: qtile/{config.py,config.d/,bin/,configs-other/,docs/}
QTILE_HOME: Final[Path] = (
    Path(__file__).resolve().parent.parent
    if (Path(__file__).resolve().parent.parent / "bin").is_dir()
    else Path.home() / ".config" / "qtile"
)
BIN_DIR: Final[Path] = QTILE_HOME / "bin"
CONFIGS_OTHER_DIR: Final[Path] = QTILE_HOME / "configs-other"
WALLPAPER_LOCK: Final[Path] = (
    Path.home() / "Pictures" / "wallpapers" / "single_screen" / "generative-orange.png"
)

# Runtime state file (replaces i3configger state for theme, bar position & font sizes)
STATE_FILE: Final[Path] = Path.home() / ".config" / "qtile" / "state.json"

# Modifiers
MOD: Final[str] = "mod4"
ALT: Final[str] = "mod1"
CTRL: Final[str] = "control"
SHIFT: Final[str] = "shift"

# Fonts (defaults from 0-basic-setup.conf & i3bar.simple.conf)
FONT_FAMILY: Final[str] = "DejaVu Sans Mono"
DEFAULT_FONT_SIZE: Final[int] = 14
DEFAULT_BAR_FONT_SIZE: Final[int] = 15
MIN_FONT_SIZE: Final[int] = 8
MAX_FONT_SIZE: Final[int] = 32
BAR_SEPARATOR: Final[str] = " ║ "

# Applications
TERMINAL: Final[str] = "xfce4-terminal"
TERMINAL_MAXIMIZED: Final[str] = "xfce4-terminal --maximize --hide-menubar"


def _clamp_font(size: int | float) -> int:
    """Clamp a font size to [MIN_FONT_SIZE, MAX_FONT_SIZE]."""
    return max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, int(size)))


@dataclass(slots=True)
class RuntimeState:
    """Persisted user preferences controlled dynamically via Mod4+w."""

    theme: ThemeName = "dark"
    bar_position: BarPosition = "bottom"
    font_size: int = DEFAULT_FONT_SIZE
    bar_font_size: int = DEFAULT_BAR_FONT_SIZE

    @classmethod
    def load(cls, path: Path = STATE_FILE) -> RuntimeState:
        """Load and validate runtime state from disk, falling back to defaults."""
        if not path.is_file():
            return cls()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return cls()
            theme = raw.get("theme", "dark")
            bar_pos = raw.get("bar_position", "bottom")
            font_size = raw.get("font_size", DEFAULT_FONT_SIZE)
            bar_font_size = raw.get("bar_font_size", DEFAULT_BAR_FONT_SIZE)
            return cls(
                theme=theme if theme in THEME_MAP else "dark",
                bar_position=bar_pos if bar_pos in ("top", "bottom") else "bottom",
                font_size=(
                    _clamp_font(font_size)
                    if isinstance(font_size, (int, float))
                    else DEFAULT_FONT_SIZE
                ),
                bar_font_size=(
                    _clamp_font(bar_font_size)
                    if isinstance(bar_font_size, (int, float))
                    else DEFAULT_BAR_FONT_SIZE
                ),
            )
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self, path: Path = STATE_FILE) -> None:
        """Persist current runtime state to disk."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except OSError:
            pass

    @property
    def color_theme(self) -> ColorTheme:
        """Return the active ColorTheme object."""
        return THEME_MAP.get(self.theme, DARK_THEME)


# ---------------------------------------------------------------------------
# State Accessor & Mutator Helpers
# ---------------------------------------------------------------------------
def get_active_theme(path: Path = STATE_FILE) -> ColorTheme:
    """Return the active ColorTheme dataclass."""
    return RuntimeState.load(path).color_theme


def get_bar_position(path: Path = STATE_FILE) -> BarPosition:
    """Return 'top' or 'bottom' for the status bar."""
    return RuntimeState.load(path).bar_position


def get_font_size(path: Path = STATE_FILE) -> int:
    """Return the active general/layout font size."""
    return RuntimeState.load(path).font_size


def get_bar_font_size(path: Path = STATE_FILE) -> int:
    """Return the active status bar font size."""
    return RuntimeState.load(path).bar_font_size


def cycle_theme(step: int = 1, *, path: Path = STATE_FILE) -> ThemeName:
    """Switch to the next/previous color theme and persist state."""
    state = RuntimeState.load(path)
    idx = THEMES.index(state.theme) if state.theme in THEMES else 0
    state.theme = THEMES[(idx + step) % len(THEMES)]
    state.save(path)
    return state.theme


def set_bar_position(position: BarPosition, *, path: Path = STATE_FILE) -> BarPosition:
    """Set bar position ('top' or 'bottom') and persist state."""
    state = RuntimeState.load(path)
    if position in ("top", "bottom"):
        state.bar_position = position
        state.save(path)
    return state.bar_position


def adjust_font_size(delta: int, *, path: Path = STATE_FILE) -> tuple[int, int]:
    """Adjust font_size and bar_font_size by `delta` points and persist state."""
    state = RuntimeState.load(path)
    state.font_size = _clamp_font(state.font_size + delta)
    state.bar_font_size = _clamp_font(state.bar_font_size + delta)
    state.save(path)
    return state.font_size, state.bar_font_size


def reset_font_size(*, path: Path = STATE_FILE) -> tuple[int, int]:
    """Reset font sizes to defaults (14pt / 15pt) and persist state."""
    state = RuntimeState.load(path)
    state.font_size = DEFAULT_FONT_SIZE
    state.bar_font_size = DEFAULT_BAR_FONT_SIZE
    state.save(path)
    return state.font_size, state.bar_font_size


# Backwards-compatible module-level aliases evaluated at import/reload time
FONT_SIZE: int = get_font_size()
BAR_FONT_SIZE: int = get_bar_font_size()


# ---------------------------------------------------------------------------
# Process & Notification Helpers
# ---------------------------------------------------------------------------
def run_detached(cmd: Sequence[str | Path] | str, *, shell: bool = False) -> None:
    """Spawn a background process safely without blocking the Qtile event loop."""
    try:
        args: Sequence[str] | str = (
            cmd if isinstance(cmd, str) else [str(part) for part in cmd]
        )
        subprocess.Popen(
            args,
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass


def notify(message: str, *, app_name: str = "CENTRAL-CONTROL-PROGRAM") -> None:
    """Send a desktop notification via notify-send."""
    run_detached(["notify-send", "-a", app_name, message])
