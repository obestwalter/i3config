# Migration from i3

## Layout

* `config` includes the partials from `config.d/` in a fixed order (variables must be defined
  before use): `palette` → `colors` → `0-basic-setup` → `1-startup` → `2-input-output` →
  `3-window-settings` → key bindings → modes → `bar`.
* i3configger is gone. Its jobs:
    * *build config from partials* → sway `include`
    * *select next/previous colors* → `bin/sway-colors.sh` (switches `config.d/colors.conf` symlink, reloads)
    * *bar position* → `bar main position top|bottom` (see `mode-sway.conf`)
    * *restart* → does not exist in sway, only `reload`
* The solarized palette moved from `0-basic-setup.conf` to `palette.conf`, because the colour scheme
  files need the palette but are included before `0-basic-setup.conf`.

## Tool replacements

| i3 / X11                          | sway / Wayland                                   |
|-----------------------------------|--------------------------------------------------|
| `i3-msg`, `i3-nagbar`             | `swaymsg`, `swaynag`                             |
| `i3bar`                           | `swaybar` (py3status unchanged)                  |
| `i3lock`                          | `swaylock`, `bin/lockdown.sh`                    |
| `xset -dpms`                      | `swayidle` (`1-startup.conf`)                    |
| `nitrogen`, `feh`                 | `output * bg ...` (`2-input-output.conf`)        |
| `unclutter`                       | `seat * hide_cursor` / `bin/toggle-unclutter.sh` |
| `xinput` touchpad                 | `input type:touchpad` / `bin/toggle-touchpad.sh` |
| `xrandr`, `arandr`                | `output ...`, `wdisplays`, `kanshi`              |
| `xbacklight`                      | `brightnessctl`                                  |
| `scrot`, `xfce4-screenshooter`    | `grim` + `slurp` (`bin/screenshot.sh`)           |
| `screenkey`                       | `wshowkeys`                                      |
| `xdotool key Menu`                | `wtype -k Menu`                                  |
| `xdotool key Escape && cmd`       | `exec cmd; mode "default"`                       |
| `xev`                             | `wev`                                            |
| `xprop`, `i3-xprop.sh`            | `bin/sway-window-info.sh` ([windows.md](windows.md)) |
| `rofi`                            | rofi with wayland support (or `wofi`, `fuzzel`)  |
| `picom`                           | not needed                                       |
| `xclip`                           | `wl-copy` / `wl-paste`                           |
| `bin/set-title.sh` (wmctrl)       | no replacement, windows cannot be retitled from outside |
| `bin/touchpad_settings.sh`        | `input type:touchpad` block, script dropped      |
| `bin/rofi-i3-ws-*.sh`             | `bin/rofi-sway-ws-*.sh`                          |
| `bin/i3-show-bindings.sh`         | `bin/sway-show-bindings.sh`                      |

## Config differences

| i3                                         | sway                                   |
|--------------------------------------------|----------------------------------------|
| `new_window normal 1px`                    | `default_border normal 1`              |
| `new_float normal 3px`                     | `default_floating_border normal 3`     |
| `popup_during_fullscreen`, `force_display_urgency_hint` | not supported, removed    |
| `exec_always dunst` (started on every restart) | `exec` (reload does not restart it) |
| `for_window [class=...]`                   | additionally `[app_id=...]` for native wayland apps |
| `move left 1 px or 1 ppt`                  | `move left 1 px` (no `ppt` for move)   |
| `tray_output primary`                      | removed (not supported)                |
| `exec --no-startup-id`                     | plain `exec`                           |

The old `mode-resize.conf` had `Control+j/k/l` bound to an incomplete `move 1 px`; fixed
to `move down/up/right 1 px`.

## Known to check after first start

* `sway -C` for config errors, `swaymsg -t get_inputs` for the touchpad/keyboard identifiers.
* `output * bg` path and monitor layout in `2-input-output.conf`.
* App specific `for_window` rules: see [windows.md](windows.md). Electron apps (Code, Slack, Teams)
  and Chrome/Firefox run native only with the right flags
  (`--ozone-platform=wayland`, `MOZ_ENABLE_WAYLAND=1`), otherwise they appear as XWayland with `class`.
* PyCharm (Java) is usually XWayland: its rules keep matching on `class`.
* `wshowkeys` needs root/input group membership.
* Workspace names contain FontAwesome glyphs, check that the font renders in swaybar.
