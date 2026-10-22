"""Startup commands executed when Qtile starts or restarts.

Converted from:
- config.d/1-startup.conf
"""

import subprocess
from libqtile import hook

from settings import BIN_DIR, CONFIGS_OTHER_DIR


def _run_background(cmd: list[str] | str, shell: bool = False) -> None:
    """Spawn a background process safely without blocking Qtile."""
    try:
        subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


@hook.subscribe.startup
def autostart_always() -> None:
    """Equivalent to i3's `exec_always --no-startup-id`."""
    # Disable DPMS power saving
    _run_background(["xset", "-dpms"])

    # Restart dunst with custom dunstrc
    dunstrc = CONFIGS_OTHER_DIR / "dunstrc"
    _run_background(
        f"pkill dunst; dunst -config {dunstrc} -markup full",
        shell=True,
    )

    # Start unclutter if not already running
    _run_background("pgrep -x unclutter || unclutter", shell=True)

    # Apply touchpad settings (check both hyphenated and underscored script names)
    touchpad_hyphen = BIN_DIR / "touchpad-settings.sh"
    touchpad_underscore = BIN_DIR / "touchpad_settings.sh"
    if touchpad_hyphen.exists():
        _run_background([str(touchpad_hyphen)])
    elif touchpad_underscore.exists():
        _run_background([str(touchpad_underscore)])

    # Restore wallpaper via nitrogen
    _run_background(["nitrogen", "--restore"])
