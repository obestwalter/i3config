# Qtile Configuration (Converted from i3wm)

This directory contains a modular [Qtile](https://qtile.org/) configuration converted from the i3wm `config` / `config.d/` setup.

## Installation

Symlink this `qtile` folder to `~/.config/qtile`:

```bash
ln -sfn "$(pwd)/qtile" ~/.config/qtile
```

Validate the configuration with Qtile:

```bash
qtile check
```

## Module Structure

| Qtile Module | i3wm Source | Description |
| :--- | :--- | :--- |
| `config.py` | `config` | Main Qtile entrypoint exporting `keys`, `groups`, `layouts`, `screens`, `mouse`, and behavior flags. |
| `settings.py` | `0-basic-setup.conf`, `i3configger.json` | Modifiers, paths, font settings, and persistent JSON state (`~/.config/qtile/state.json`) for theme & bar position. |
| `colors.py` | `0-basic-setup.conf`, `colors.0-dark.conf`, `colors.1-light.conf` | Full Solarized color palette and Dark/Light themes. |
| `startup.py` | `1-startup.conf` | `@hook.subscribe.startup` hook running `xset -dpms`, `dunst`, `unclutter`, `touchpad-settings.sh`, and `nitrogen --restore`. |
| `groups.py` | `0-basic-setup.conf`, `3-window-settings.conf` | Workspaces `1`–`10` with FontAwesome labels, window title icon rules, floating rules, sticky windows (`Control+F12`), and arbitrary window scratchpad (`Shift+F12` / `F12` / `Mod4+Return`). |
| `layouts.py` | `0-basic-setup.conf` | `Max` (default tabbed equivalent), `Columns` (split), `Stack` (stacking), `TreeTab`, and `Floating` (`3px` border). |
| `keys.py` | `control-main-key-bindings.conf`, `mode-*.conf` | All navigation, window manipulation, media keys, Rofi launchers, and `KeyChord` modes (`Mod4+c`, `Mod4+w`, `Mod4+r`). |
| `bar.py` | `i3bar.simple.conf`, `i3bar.full.conf`, `py3status/` | Built-in Qtile bar & widgets (`GroupBox`, `Chord`, `TaskList` with window icons, `sysdata`, `wifi`, `uname`, `diskdata`, `online_status`, `volume_status`, `battery_level`, `tztime`, `Systray`). |
