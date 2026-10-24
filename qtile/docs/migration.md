# Migration from i3

Structure: see [../README.md](../README.md). The architecture, gotchas and the runtime controls are in [qtile.md](qtile.md).

## What replaces what

| i3                                  | qtile                                                          |
|-------------------------------------|----------------------------------------------------------------|
| `config`, `i3configger`             | `config.py` + `config.d/*.py`, colours/bar/fonts via `RuntimeState` (`~/.config/qtile/state.json`) |
| `i3-msg`                            | `qtile cmd-obj`, `qtile shell`, `InteractiveCommandClient`     |
| `i3bar` + `py3status`               | Qtile `bar` + widgets (`config.d/bar.py`, no py3status)        |
| `for_window [class=...]`            | `Match(...)` rules in `groups.py` (`FORCE_TILE_MATCHES`, `TitleIconRule`) |
| `title_format` icons                | `format_window_title` in `groups.py` (applied by the TaskList) |
| scratchpad, `sticky`                | `WindowStateTracker` + hidden group `_i3_scratchpad`, DropDown terminal |
| modes (`mode "..."`)                | `KeyChord` (`mode=False` single shot, `mode=True` persistent)  |
| `xdotool key Escape && cmd`         | not needed with single shot chords                             |
| `i3-xprop.sh`                       | `bin/qtile-window-info.sh`                                     |
| `i3-show-bindings.sh`               | `bin/qtile-show-bindings.sh`                                   |
| `rofi-i3-ws-*.sh`                   | `bin/rofi-qtile-ws-*.sh`                                       |
| `i3configger-wrapper.sh`            | dropped                                                        |
| `workspace_layout tabbed`           | `Max` layout + TaskList (approximation, no real tab bar)       |
| `layout stacking`, `toggle split`   | `Stack`, `Columns`                                             |
| `focus mode_toggle`                 | `focus_mode_toggle` lazy function                              |
| `move workspace to output next`     | `move_workspace_to_next_screen` lazy function                  |

## X11 tools

Qtile's X11 backend works with the same X11 tools as i3, so these scripts are shared (copied) and unchanged:
`rofi-file-browser.sh`, `screenshot-and-gwenview.sh`, `toggle-screenkey.sh`, `toggle-touchpad.sh`,
`toggle-unclutter.sh`, `touchpad_settings.sh`, `lockdown.sh`, `set-title.sh`.
If you want to run Qtile with its Wayland backend these need the replacements described in `../../sway/docs/migration.md`.

## Moved files

* `bin/rofi-qtile-ws-list.sh`, `bin/rofi-qtile-ws-move.sh` moved from the i3 `bin/` to `qtile/bin/`.
* The Python modules moved from `qtile/` to `qtile/config.d/`, the architecture guide from `qtile/README.md` to `qtile/docs/qtile.md`.
* `settings.py`: `I3_HOME`/`REPO_ROOT` replaced by `QTILE_HOME` (the qtile folder, fallback `~/.config/qtile`),
  `BIN_DIR` and `CONFIGS_OTHER_DIR` now point into the qtile folder.

## Not ported

* `py3status/` modules and `i3bar.*.conf`: replaced by `bar.py`. The `ob_bofh_excuse` module has no equivalent.
* `i3configger.json`, `config.d/i3bar.*.conf`, `mode-i3configger.conf` (replaced by the `Mod4+w` mode).
