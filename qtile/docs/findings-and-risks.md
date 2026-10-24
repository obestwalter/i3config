# Findings, shortcomings and risks

Everything noticed while restructuring the qtile folder to mirror the i3 layout, including potential problems.

> [!IMPORTANT]
> Verified: the 4 tests in `test_qtile_config.py` pass after the restructuring, and `bin/qtile-window-info.sh` was run
> against a faked `xprop`. **Not verified: anything against a real Qtile** (`qtile check`, a real session, the real
> `libqtile` API). The tests use a stub of `libqtile`, so they prove load/reload structure and state handling,
> not that widgets, keys or layouts are accepted by the installed Qtile version.

## Restructuring changes and their risks

| Change | Risk |
|--------|------|
| Modules moved from `qtile/` to `qtile/config.d/`, `config.py` puts `config.d` on `sys.path` (a dir with a dot cannot be a package). | Module names are generic top-level names (`colors`, `settings`, `keys`, `groups`, `layouts`, `bar`, `startup`) inserted at `sys.path[0]`. They can shadow, or be shadowed by, other top-level modules in Qtile's process (own or third party). Same risk existed before with `qtile/` on the path. A package-style rename (e.g. `ob_qtile.colors`) would remove it. |
| `settings.py`: `I3_HOME`/`REPO_ROOT` → `QTILE_HOME`; `BIN_DIR`/`CONFIGS_OTHER_DIR` now in the qtile folder. | `QTILE_HOME` is derived from `Path(__file__).resolve()`: works for a symlinked `~/.config/qtile`. If `config.d/` is copied alone (without `bin/`) the fallback `~/.config/qtile` is used and scripts may be missing. |
| `rofi-qtile-ws-*.sh` moved from the i3 `bin/` into `qtile/bin/`. | Anything outside this repo that references `~/.i3/bin/rofi-qtile-*` breaks. |
| Scripts duplicated into `qtile/bin/` (and `sway/bin/` for the Wayland ones). | Fixes need to be applied in several copies until the i3 folder is retired. |
| Architecture guide moved from `qtile/README.md` to `qtile/docs/qtile.md`; README rewritten. | The old `docs/qtile.md` link in the earlier README no longer exists. `docs/qtile.md` at the repo root was absent when the restructuring started (it was not tracked), so the guide in `qtile/docs/` is the only copy. |
| `py3status/` and `i3bar.*.conf` **not** copied. | Intentional (bar.py replaces them), but the structure is not a 1:1 mirror. The `ob_bofh_excuse` module has no replacement. |
| `i3configger` files not mirrored. | Replaced by `RuntimeState`/`Mod4+w`. State is in `~/.config/qtile/state.json`, outside the repo and not versioned. |
| Tests stay at `qtile/test_qtile_config.py`. | `REPO_ROOT` in the test is `parent.parent` (repo root) and `QTILE_DIR = repo/qtile`; the tests break if the qtile folder is moved elsewhere. The i3 side has no tests. Discovery: `python3 -m unittest discover -s qtile` from the repo root, or `-s .` inside `qtile/`. |

## Config problems (pre-existing, found while reading)

### Behaviour differences to i3
* `workspace_layout tabbed` is approximated by `Max` + `TaskList`; there is no real tab bar per window group, and
  `focus_direction` cycles windows for left/up and right/down, which differs from i3 tabbed navigation in edge cases.
* **Sticky windows** are emulated: the `setgroup` hook moves every tracked sticky window to the new group, which can flicker
  and re-layout, and the state (`TRACKER`) is lost when Qtile restarts (`lazy.restart()`), only `reload_config` keeps it.
* **Scratchpad** is emulated with a hidden group `_i3_scratchpad` plus a DropDown terminal. `F12`, `Mod4+Return` share
  the logic: with a window in the dynamic scratchpad the DropDown terminal is not reachable.
* The scratchpad windows and sticky windows are tracked by `wid`; after a restart, X11 window ids stay but the tracker is empty.
* `Key([MOD], "period", lazy.hide_show_bar())` hides the bar on the current screen only, i3's `bar mode toggle` affects all outputs of that bar.
* `lazy.screen.toggle_group()` (Alt+Tab) goes back to the previous group of that screen, equal to `workspace back_and_forth`
  only when `workspace_auto_back_and_forth` semantics are not needed.
* `step_visible_group` (workspace prev/next) wraps around; i3's `workspace prev/next` also skips empty workspaces only if
  `workspace prev_on_output` is used, so behaviour differs for empty workspaces.
* `move_workspace_to_next_screen` cycles all screens (the i3 FIXME is still there).
* `resize_window` / `move_window_by` in tiling layouts call layout specific methods (`grow_*`, `shuffle_*`), step sizes
  (100/10/1 px) are only honoured for floating windows. For tiled windows each key press is one layout step.

### Startup and reload
* `autostart_always` is a `@hook.subscribe.startup` hook, which also runs after `reload_config` (theme switch, bar move, font
  scaling use reload). Each reload therefore runs `pkill dunst; dunst ...`, `nitrogen --restore` and the touchpad script again.
  A pending notification (e.g. "theme switched") may be killed by the dunst restart. Using `startup_once` for dunst/unclutter
  would avoid it.
* `xset -dpms`, `unclutter`, `nitrogen`, `touchpad-settings.sh` are X11 tools: on the Wayland backend none of them work.
* The script lookup in `startup.py` accepts both `touchpad-settings.sh` and `touchpad_settings.sh`. The i3 config refers
  to the hyphenated name but the file is underscored, so the **i3 config calls a non-existing script**.
* `touchpad_settings.sh` hardcodes the device `VEN_0488:00 0488:104B Touchpad`: other machines need another name.

### Keys
* `lazy.spawn("xbacklight e -ctrl intel_backlight ...")` (typo-like `e` argument carried over from i3) is probably not a valid xbacklight command line; `brightnessctl` or `xbacklight -ctrl intel_backlight -dec 5` should be checked.
* The volume keys do not signal the bar (`killall -SIGUSR1 py3status` is gone), the bar polls instead; changes appear with delay.
* `Key([MOD], "y", lazy.spawn("xdotool key Menu"))` is a press (not `--release`) binding, so the Super key is still held while `Menu` is sent,
  which many applications interpret as `Super+Menu`. The i3 config uses `bindsym --release`.
* The `KeyChord` named modes show the whole help text as the mode name in `widget.Chord`, this can be wider than the bar.
* The `CENTRAL-CONTROL-PROGRAM` chord uses `scrot` (X11), the `s` binding runs `i3lock ... && systemctl suspend` (i3 ran suspend and lock in parallel).
* `i3lock -t -i` needs a PNG file at `~/Pictures/wallpapers/single_screen/generative-orange.png`.
* Keysyms like `numbersign`, `udiaeresis`, `asciicircum` assume the German layout.

### Window rules
* Rules only match X11 `WM_CLASS`: `format_window_title` uses `window.get_wm_class()`, which is not available on Wayland windows (use `app_id`).
* `ICON_CLASS_RULES` for `.*terminal.*` is broad (also matches e.g. `Gnome-terminal`, `xfce4-terminal`, but also unrelated classes).
* `FORCE_TILE_MATCHES` is applied in `client_new` by setting `window.floating = False`; Qtile may re-evaluate floating rules
  (`float_rules`) after this hook, so dialogs for Zoom/FreeRDP may still float. Needs a real test.
* PyCharm specific rules (borders, dialog placement, diff view hack) were not ported (they are commented out in i3 as well).
* `wmname = "LG3D"` is needed for Java apps, but breaks tools that rely on `_NET_SUPPORTING_WM_CHECK` names (e.g. some screen recorders).
* `FontAwesome` glyphs in workspace names and title icons are private-use characters that are easily corrupted by editors or encodings.

### Bar
* `bar.py` reads `/proc` and `/sys` itself. Battery path, wifi interface name, `intel_backlight` etc. are machine specific.
* Widgets depend on the Qtile version (`widget.GenPollText`/`func` signature, `Systray` vs `StatusNotifier`, `TaskList` options, `Chord` names).
* On Wayland Qtile, `Systray` is not available (use `StatusNotifier`).
* `on_click` actions of the py3status modules (`glances`, `htop`, `speedtest-cli`, `nmtui`) were not ported unless handled in `bar.py` (not checked).
* The font scaling (`Mod4+w`, `Shift+arrows`) works only through reload and rescales fixed bar height proportionally; a reload also restarts dunst (see above).

## Scripts

| Script | Notes |
|--------|-------|
| `qtile-window-info.sh` | New. X11 only for the click mode (xprop). `focused` uses `qtile cmd-obj -o window -f info`, output format depends on the Qtile version. Title quoting is as bad as in `i3-xprop.sh` (xprop does not escape quotes). Pick mode only tested against faked xprop output. |
| `qtile-show-bindings.sh` | New. Uses `qtile cmd-obj -o root -f display_kb`: **the command name was not verified** against a Qtile install (it may be `display_kb` on the `cmd` object in some versions: try `qtile cmd-obj -o cmd -f display_kb`). Only prints bindings of the running Qtile. |
| `rofi-qtile-ws-list.sh`/`-move.sh` | Call `python3 -c 'from libqtile...'`: the `python3` in `PATH` must be the one with Qtile installed (fails silently for a pipx/venv Qtile, output is sent to `/dev/null`). Prefix matching `name.strip().startswith(target.strip())` can match the wrong workspace for `1` vs `10`. |
| `rofi-file-browser.sh` | Unchanged copy, `coproc ( ... )` fails `bash -n` on bash 3 (macOS), works on bash 4+. |
| `toggle-screenkey.sh`, `toggle-touchpad.sh`, `toggle-unclutter.sh`, `lockdown.sh`, `screenshot-and-gwenview.sh`, `touchpad_settings.sh`, `set-title.sh` | Unchanged copies of the i3 versions (X11 tools: xinput, xdotool, scrot, i3lock, wmctrl, screenkey, unclutter). `set-title.sh` uses `wmctrl`/`xprop` and works for X11 windows regardless of the window manager. |
| not copied: `i3-xprop.sh`, `i3-show-bindings.sh`, `i3configger-wrapper.sh`, `rofi-i3-ws-*.sh`, `bin/inactive/*` | i3 specific. `bin/inactive/*` (i3ipc based) does not work with Qtile. |

## Environment
* Qtile packages in distros are often old; the config uses Python >= 3.10 syntax (`X | Y` types, `slots=True` dataclasses), as in `settings.py`.
* `qtile check` validates syntax and imports only.
* `install-dependencies.sh` uses Debian/Ubuntu package names and was not run. `qtile` from apt can be an old version,
  where `lazy.hide_show_bar`, `KeyChord(mode=...)` or `DropDown` options differ.
* Fonts: `DejaVu Sans Mono` and `FontAwesome` must be installed; Qtile (pango/cairo) does not use the i3 `pango:` font string.
* No compositor is started (`picom` was commented out in i3); `DropDown(opacity=0.95)` needs one for transparency.

## Verification checklist
1. `qtile check` with the folder symlinked to `~/.config/qtile`.
2. Start a session (`startx` with `qtile start`, or Xephyr: `Xephyr -screen 1280x800 :1 & DISPLAY=:1 qtile start`).
3. Check `~/.local/share/qtile/qtile.log` for errors in widgets, keys and layouts.
4. Test the modes `Mod4+c`, `Mod4+w`, `Mod4+r`, each `Mod4+w` action (reload keeps sticky/scratchpad state).
5. Open the apps with title/float rules and compare with `bin/qtile-window-info.sh` output.
6. Check `bin/qtile-show-bindings.sh` against `bin/i3-show-bindings.sh` output.
7. Run the tests: `python3 -m unittest discover -s qtile -v`.
