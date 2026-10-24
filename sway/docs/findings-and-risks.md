# Findings, shortcomings and risks

Everything learned while porting the i3 setup to sway, including problems that are only potential.

> [!IMPORTANT]
> The port was written on macOS without sway installed. **Nothing was run against a real sway.**
> The only thing exercised was the jq logic of `bin/sway-window-info.sh`, against a mocked `swaymsg`.
> First step on the target machine: `sway -C` (validate config), then start sway from a TTY and read stderr.

## Verified vs. unverified

| Item | Status |
|------|--------|
| `bin/sway-window-info.sh` jq filters (`focused`, `all`) | tested with mocked `swaymsg` output |
| `pick` mode of `sway-window-info.sh` (slurp + rect matching) | **untested**, fiddly (see below) |
| Bash syntax of the other scripts | `bash -n` only; shellcheck not available |
| All config.d partials | **untested**, written by transforming the i3 files |
| Config option names/syntax (`default_border`, `seat * hide_cursor`, `output * power off`, `events toggle enabled disabled`, `bar main position`) | from knowledge of sway(5), not checked against the installed version |

## Config problems

### Include order / variables
* Variables must be defined before use in sway. i3configger resolved this by ordering partials.
  Now `config` includes them explicitly: palette → colors → 0-basic-setup → ... .
  Adding a new partial that uses a variable defined later will fail at load time.
* `colors.conf` is a **symlink** (`colors.0-dark.conf`). It is created by hand in the repo.
  A checkout on a system without symlink support (or a copy via some tools) breaks it, and `include` fails.
  `sway-colors.sh` replaces the symlink, so the repo working tree becomes dirty after switching colors.
* `include /etc/sway/config.d/*` is at the end. Distro snippets there can override or conflict with settings
  (e.g. they set up systemd/dbus environment, which is wanted, but may also start things like a bar or
  idle daemon on some distros). Check `ls /etc/sway/config.d`.
* The `include` of a path with a relative name is resolved relative to the including file. Fine for
  `~/.config/sway/config`; if sway is started with `-c some/other/config` the same holds, but
  `$swayHome` (`~/.config/sway`) is hardcoded for scripts, bar and dunst. Moving the folder needs a change there.
* The solarized palette was moved out of `0-basic-setup.conf` into `palette.conf`. The i3 side still has
  it inside, so the two folders have diverged structurally.

### Options removed or changed
* `popup_during_fullscreen`, `force_display_urgency_hint` and `tray_output primary` are not supported
  by sway and were dropped (behaviour change: no urgency hint timeout, tray on all/default outputs).
* `new_window normal 1px` → `default_border normal 1`, `new_float normal 3px` → `default_floating_border normal 3`.
  Same visual intent, but not identical semantics in edge cases (sway applies borders to different
  window types than i3's `new_window` in some versions).
* `workspace_layout tabbed`, `focus_on_window_activation smart`, `hide_edge_borders smart`,
  `mouse_warping output`, `floating_modifier` are kept; they exist in sway but are unverified here.
* `exec --no-startup-id` was replaced with plain `exec`; startup notification does not exist in sway.
* `move left 1 px or 1 ppt` is not valid for sway's `move` (no `ppt`); converted to `px` only.
  `resize ... px or ... ppt` is still valid.
* Pre-existing bug in the i3 `mode-resize.conf` (fixed only in `sway/`): `Control+j/k/l` bound to
  `move 1 px or 1 ppt` without a direction. The i3 folder still has it.

### Key bindings
* `bindsym $win+Shift+numbersign kill`, `asciicircum`, `udiaeresis` rely on the **German layout** being
  set via `xkb_layout de`. If the keyboard identifier/layout is wrong, these bindings silently do not
  match. Use `wev` to verify keysyms.
* `bindsym --release $win+y exec wtype -k Menu`: `wtype` needs the compositor to support the
  virtual-keyboard protocol (sway does) but some apps ignore synthetic `Menu` keys.
* `bindsym $win+period bar mode toggle` and `mode-sway.conf` use `bar main ...`. This relies on the bar `id main`
  in `bar.conf`. Renaming the id breaks the mode bindings.
* `bindsym F11 fullscreen`, `F12 scratchpad show` etc. are global; unchanged from i3.
* `$win+Return scratchpad show` in sway behaves like i3, but the scratchpad is empty after login.
* `XF86Audio*` bindings call `pactl` and `killall -SIGUSR1 py3status`. Works with PipeWire's
  pulse compatibility; the original comment "default sink seems to change randomly" still applies. The `&&`
  was changed to `;` so the signal is sent even if `pactl` fails, which is a (small) behaviour change.
* `brightnessctl set 5%-` needs write access to the backlight (udev rule or `video` group). The old
  command named the `intel_backlight` device explicitly; now the default device is used.

### Modes
* The `xdotool key Escape` trick is gone; modes are left with `; mode "default"`.
  If an `exec` command in a mode fails, the mode is still left (same as before).
* `bar main position top|bottom` in `mode-sway.conf` replaces the i3configger `shadow` mechanism. The
  position is **not persisted**: a reload resets it to the value in `bar.conf` (`bottom`).
* There is no `restart` in sway. The i3 mode's "restart" entry was removed. A reload does not restart
  `swaybar`/`py3status` reliably in all cases.
* `swaynag -B 'Yes' 'swaymsg exit'`: the nag button syntax differs slightly between versions of swaynag
  (older: `-b`). Check `swaynag --help`.

### Startup
* `swayidle` lock/DPMS timeouts (10/15 min) are **new** choices; the i3 setup only had `xset -dpms`
  (i.e. DPMS disabled). If screens should never blank, remove the `swayidle` block.
* `swayidle` command lines use `swaymsg "output * power off"`; older sway (< 1.7) only knows `dpms off`.
* Every config reload re-runs `exec_always`-style lines only; here `dunst` and `swayidle` use `exec`, so they
  start only once per session. Changes to those lines need a re-login (or a manual restart).
* `$lockCommand` is expanded inside single quotes in the `swayidle` line. Variables are substituted by sway
  before the shell sees them, so it works, but a command containing `'` would break it.
* The `picom` note in the i3 startup file is not carried over: no compositor needed. Blur/shadows/transparency
  would need SwayFX or sway >= 1.11.
* `xset -dpms`, `unclutter`, `nitrogen --restore`, `touchpad-settings.sh` have no direct Wayland equivalent and
  were replaced by native config (`2-input-output.conf`).

### Input / output
* `input type:keyboard` and `type:touchpad` apply to **all** devices of that type. The original script
  targeted one named device (`VEN_0488:00 0488:104B Touchpad`). If a second touchpad/trackpoint exists, use
  the identifier from `swaymsg -t get_inputs`.
* `drag_lock enabled` and `tap enabled`: valid values depend on the sway version (`drag_lock enabled|disabled`
  in newer versions; very new versions also accept `enabled_sticky`).
* `seat * hide_cursor 1000` hides the cursor only after the timer; it does not replicate unclutter's
  `--ignore-scrolling`. Some apps (games, Xwayland clients) may bring the cursor back.
* The wallpaper path is carried over from the i3 config and must exist, else the background is plain.
* Monitor layout (`xrandr` scripts in `bin/inactive/`) was **not** ported. `2-input-output.conf` has only
  commented examples. `kanshi` is the usual tool for dock/undock profiles. `move workspace to output next`
  is kept (including the FIXME that it cycles through all monitors).

### Window rules
* Native Wayland windows have `app_id` and no `class`/`instance`; XWayland windows have `class`/`instance`
  and no `app_id`. Every rule therefore exists twice (class + app_id).
* The `app_id` values in `3-window-settings.conf` are **guesses** (e.g. `org.kde.gwenview`, `org.kde.krusader`,
  `(?i)slack`, `(?i)thunderbird`, `code`). They were not checked against running apps. Use
  `bin/sway-window-info.sh` to confirm and fix them.
* The terminal rule `class="(.*)terminal(.*)"` is duplicated for `app_id`. This is a very broad regex.
* Rules using `instance` (Code, Chrome, Teams, Zoom) lose it in the `app_id` twin: `app_id` rules are
  therefore slightly broader than the class rules.
* `window_role` does not exist for native windows; `xprop`-style `WM_WINDOW_ROLE` criteria cannot be used.
* PyCharm/Java apps usually run via XWayland (unless the JetBrains Runtime Wayland flag is enabled). Dialog
  and "diff view hack" rules based on `sun-awt-X11-XDialogPeer` are commented out in the config; if enabled again they
  only work for XWayland, and window title patterns containing `/home/` paths are untested.
* Electron apps (Code, Slack, Teams) and Chrome/Firefox choose Wayland or XWayland depending on flags
  (`--ozone-platform=wayland`, `MOZ_ENABLE_WAYLAND=1`). The same app can match different rules
  depending on how it is launched.
* `title_format` icon strings contain FontAwesome private-use glyphs. These survived the copy but are
  invisible in many editors/terminals and easy to corrupt (encoding, copy/paste).
* Workspace names also contain glyphs and `|`, and are used as identifiers in `assign`, bindings
  and the rofi scripts; any glyph change breaks all references. Fonts must render them in `swaybar`
  (`FontAwesome` version matters: v5 vs v6 codepoints differ).

## Scripts

| Script | Problems |
|--------|----------|
| `sway-window-info.sh` | `pick` mode is a workaround: `slurp` has no "pick a window" mode, so it lets the user select a rectangle from all window rects and uses its top-left corner for lookup. Overlapping/floating windows can give the wrong window; selecting by clicking exactly on a window rect is required. `focused` is the reliable mode. Needs `jq`, `swaymsg`, `slurp`. |
| `sway-show-bindings.sh` | Only greps `bindsym` lines at line start in `config.d/*.conf`; bindings inside `mode` blocks are indented and **not listed** (same limitation as the i3 script on the generated config for modes). Variables are only partly substituted (`$win`, `$alt`; `$bin`, `$ccp` etc. stay literal). |
| `rofi-sway-ws-*.sh` | Rely on rofi's script mode and on workspace names with glyphs being passed back intact. `sort -V` ordering works because names start with a number. Needs wayland-capable rofi, otherwise rofi falls back to XWayland and may not show/grab focus properly. |
| `screenshot.sh` | Saves into `$HOME` (like before) and copies to clipboard; no failure handling if `grim` is missing. `region` aborts if `slurp` is cancelled. |
| `screenshot-and-gwenview.sh` | Needs gwenview (KDE); bound to a bar right-click. |
| `toggle-screenkey.sh` | `wshowkeys` needs root/setuid or `input` group membership to read keyboard devices; may not be packaged on every distro. Options `-a bottom -m 20` are untested. |
| `toggle-touchpad.sh` | Uses `events toggle enabled disabled`; reads state back via `.libinput.send_events` which can differ per version/device. With several touchpads only the first is reported. The old script also moved the mouse pointer away (xdotool), not possible on Wayland. |
| `toggle-unclutter.sh` | State is kept in `/tmp/sway-hide-cursor`; after a reboot/re-login the file is gone, the initial state is "on" (from config) while the toggle thinks "off" is the next step if the file is missing, so the first toggle can be a no-op visually. |
| `lockdown.sh` | Uses `convert` (ImageMagick 6; v7 prefers `magick`). Screenshot in `/tmp` is briefly world-readable. Not wired to any binding (like in i3). Multi-monitor: `swaylock -i` with a single image is applied to all outputs. |
| `sway-colors.sh` | Uses `readlink -f` and glob ordering of `colors.[0-9]*.conf`. `readlink -f` is GNU, not on macOS (fine for the target Linux). A broken/missing symlink selects index 0. Changes a tracked symlink. |
| `rofi-file-browser.sh` | Copied unchanged; contains `coproc ( ... )` constructs that fail `bash -n` on bash 3 (macOS). Works with bash 4+. Uses `xdg-open`, fine on Wayland. |
| not ported: `set-title.sh` | Uses `wmctrl`/`xdotool` to rename a window. No equivalent: Wayland clients own their titles. Possible alternative: `title_format` via `for_window` + mark, only changes the decoration. |
| not ported: `touchpad_settings.sh` | Replaced by the `input type:touchpad` block. |
| not ported: `i3-xprop.sh` | Replaced by `sway-window-info.sh`. |
| not ported: `bin/inactive/*` | Python/`i3ipc` helpers (workspace swapping, quickswitch, ...), xrandr scripts. i3ipc-python also speaks sway IPC, so many may work with small changes, but they were not reviewed. |
| not ported: `rofi-qtile-*` | Out of scope (qtile ignored). |

## Status bar
* `swaybar` + `py3status` should work (`output_format = "i3bar"`), but untested. py3status detects the window manager
  through the environment (`SWAYSOCK`); if detection fails, modules that use the IPC may break.
* `i3bar.full.conf`/`i3bar.clock.conf` are copies of the generated files in the repo root.
  They are **not** generated any more; i3configger templating (`i3bar.tpl.conf`, colors substitution) was dropped. Colours
  in `bar.conf` are written with the palette variables instead.
* `on_click` entries still call `xfce4-terminal` (works on Wayland, but is a GTK app that may start via XWayland).
  `nmtui`, `htop`, `glances`, `speedtest-cli` need to be installed.
* The tray: `swaybar` implements the StatusNotifier protocol only. Old XEmbed tray icons (many legacy apps) do not show up.
* Bar `modifier $win` and button bindings (`button3`, `button4/5 nop`) are the same as before.
* Log file `/tmp/py3status.swaybar.log` replaces the per-output log of i3configger; `.gitignore` entries for `py3status.*.log` in the
  repo root do not apply to `/tmp`.
* The `dbus-notify` option and battery/cpu modules in `py3status/` were not reviewed for X11 dependencies.

## Environment problems
* Sway needs to be started from a TTY/display manager with a session file; **no X11 session**
  tools (xinput, xdotool, xprop, xev, xrandr, xclip, scrot, i3lock, screenkey, unclutter, nitrogen) work for native windows.
* XWayland-only tools still run but only see XWayland windows: `xdotool`, `wmctrl`, `xprop` give wrong or partial results.
* Clipboard: `xclip`/`xsel` only work for XWayland; use `wl-copy`/`wl-paste`. Clipboard managers (`TODO` in key bindings) need
  `wl-paste --watch` + `cliphist`; no clipboard manager is set up (commented line in `1-startup.conf`).
* Global shortcuts, screen sharing and screen recording need `xdg-desktop-portal-wlr` (+ PipeWire). **Not in
  `install-dependencies.sh`** -> Zoom/Teams/Chrome screen sharing will not work without it. Also missing: `polkit` agent,
  `xdg-desktop-portal-gtk`, and `XDG_CURRENT_DESKTOP=sway` environment export (distro `/etc/sway/config.d` usually handles this).
* Remote desktop: `FreeRDP`/`xfreerdp` run through XWayland (rules for `xfreerdp` keep matching on `class`);
  `wlfreerdp`/`sdl-freerdp` use `app_id`.
* NVIDIA proprietary drivers: sway needs `--unsupported-gpu` and has known problems; the setup used an Intel iGPU
  (`intel_backlight`), where this is not an issue.
* `install-dependencies.sh` uses Debian/Ubuntu package names (`wshowkeys`, `wtype`, `rofi` with wayland support and
  `swaylock` availability vary by release). The original script also was apt-only.
* Package versions: sway < 1.7 lacks `output power`, < 1.8 lacks some `input` options; the `include` directive needs
  sway >= 1.5.
* `$swayHome` is `~/.config/sway`, whereas i3 used `~/.i3`. Hardcoded absolute paths from the i3 config
  (`/home/oliver.bestwalter/_sys/bin/i3configger`) were removed along with the i3configger mode.

## Documentation / repo state
* `sway/mkdocs.yml` is separate from the root `mkdocs.yml`. Neither includes the other, so both doc sets are built independently.
* The root `docs/` mention i3-only tooling (`i3configger`, xprop); these are not updated.
* The `sway/` copies of `py3status/`, `configs-other/` and `i3bar.*.conf` duplicate files. Until i3 is retired, fixes need
  to be applied twice (or one side symlinked).
* `configs-other/picom.conf` was intentionally not copied.
* `dunstrc`/`config.rasi` were copied unchanged. The rofi theme/config is not wayland-specific, but font sizes depend on
  scaling (`output ... scale`), which is not set.
* HiDPI: X11 `Xft.dpi` style scaling is gone; scaling is per output in sway. Fonts set in the bar and `font` (14/15 pt) will look different
  than on X11 depending on scale.
* Git status when this was written: `sway/` was untracked (not committed). The repo also has unrelated modified
  `qtile/*` files and untracked `docs/qtile.md` and `tests/` which are outside this port.

## Suggested verification checklist
1. `sway -C -c sway/config` (use a copy at `~/.config/sway`, since paths are absolute to it).
2. Start sway, check the log: `sway -d 2> /tmp/sway.log`.
3. `swaymsg -t get_inputs` / `get_outputs`, adjust `2-input-output.conf`.
4. Open every app that has a rule, run `bin/sway-window-info.sh focused`, fix `app_id` values.
5. Test each binding mode: `$win+c`, `$win+w`, `$win+r`.
6. Check bar, py3status modules, tray icons, glyph rendering.
7. Screenshots, lock, idle, suspend, screen sharing.
8. Compare `bin/sway-show-bindings.sh` output with the i3 one to detect lost bindings.
