"""Startup commands executed when Qtile starts or restarts.

Converted from:
- config.d/1-startup.conf
"""

from __future__ import annotations

from libqtile import hook

from settings import BIN_DIR, CONFIGS_OTHER_DIR, run_detached


@hook.subscribe.startup
def autostart_always() -> None:
    """Equivalent to i3's `exec_always --no-startup-id`."""
    # Disable DPMS power saving
    run_detached(["xset", "-dpms"])

    # Restart dunst with custom dunstrc
    dunstrc = CONFIGS_OTHER_DIR / "dunstrc"
    run_detached(
        f"pkill dunst; dunst -config {dunstrc} -markup full",
        shell=True,
    )

    # Start unclutter if not already running
    run_detached("pgrep -x unclutter || unclutter", shell=True)

    # Apply touchpad settings (check both hyphenated and underscored script names)
    for script_name in ("touchpad-settings.sh", "touchpad_settings.sh"):
        script_path = BIN_DIR / script_name
        if script_path.is_file():
            run_detached([script_path])
            break

    # Restore wallpaper via nitrogen
    run_detached(["nitrogen", "--restore"])
