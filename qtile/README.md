# Qtile Configuration & Migration Guide

This document describes the architecture, design decisions, and lessons learned from converting the `i3wm` + `i3configger` + `py3status` setup into a native, modular [Qtile](https://qtile.org/) configuration under `qtile/`.

---

## 1. Quick Start & Installation

Symlink the `qtile/` package to `~/.config/qtile`:

```bash
ln -sfn "$(pwd)/qtile" ~/.config/qtile
```

Validate syntax and configuration with Qtile:

```bash
qtile check
```

Run the unit and architecture test suite (works on any machine, even without X11 or `libqtile` installed):

```bash
python3 -m unittest discover -s tests -v
```

---

## 2. Architecture & Mapping from i3wm

In `i3wm`, the configuration is a static text file. Achieving modularity, shared color variables, and dynamic bar/theme switching required an external build tool ([`i3configger`](https://github.com/obestwalter/i3configger)) to merge `config.d/*.conf` partials, interpolate variables, write out `config` and `i3bar.*.conf`, and invoke `i3-msg restart`.

Because Qtile's configuration is **native Python**, all build-time templating is replaced by clean runtime data structures and modular imports:

```
qtile/
├── config.py      # Entrypoint: reloads submodules in dependency order & exports Qtile settings
├── colors.py      # Immutable ColorTheme dataclass + Solarized DARK_THEME & LIGHT_THEME
├── settings.py    # Paths, constants, process helpers, and RuntimeState (state.json)
├── startup.py     # @hook.subscribe.startup (xset, dunst, unclutter, touchpad, nitrogen)
├── groups.py      # Workspaces 1..10, WindowStateTracker (scratchpad/sticky), title icons
├── layouts.py     # Max (tabbed), Columns (split), Stack, TreeTab, and Floating layouts
├── keys.py        # Keybindings, mouse bindings, and KeyChord modes (Mod4+c, Mod4+w, Mod4+r)
└── bar.py         # SystemStatusPoller (/proc & /sys) and built-in Qtile bar widgets
```

| i3wm Source | Qtile Module | How It Works Now |
| :--- | :--- | :--- |
| `config` | `qtile/config.py` | Main entrypoint loaded by Qtile (`libqtile.confreader`). |
| `0-basic-setup.conf`, `i3configger.json` | `qtile/settings.py` | `RuntimeState` dataclass persists theme, bar position, and font sizes in `~/.config/qtile/state.json`. |
| `colors.0-dark.conf`, `colors.1-light.conf` | `qtile/colors.py` | `ColorTheme` (`@dataclass(frozen=True, slots=True)`) provides type-safe color access (`theme.cfbg`, `theme.background`). |
| `1-startup.conf` | `qtile/startup.py` | `autostart_always()` registered via `@hook.subscribe.startup`. |
| `3-window-settings.conf` | `qtile/groups.py` | `TitleIconRule` regex rules prefix FontAwesome icons; `FORCE_TILE_MATCHES` enforces tiling on Zoom/FreeRDP. |
| `control-main-key-bindings.conf`, `mode-*.conf` | `qtile/keys.py` | Keybindings and `KeyChord` modes (`CENTRAL-CONTROL-PROGRAM`, `qtile-config`, `resize / move`). |
| `i3bar.simple.conf`, `i3bar.full.conf`, `py3status/` | `qtile/bar.py` | `SystemStatusPoller` reads `/proc` and `/sys` directly using `pathlib.Path` with zero external pip dependencies. |
| `bin/rofi-i3-ws-*.sh` | `bin/rofi-qtile-ws-*.sh` | Uses `libqtile.command.client.InteractiveCommandClient` instead of `i3-msg`. |

---

## 3. Key Lessons Learned & Qtile Gotchas Solved

### 3.1 Submodule Caching & Hook Loss During `qtile.reload_config()`

**The Problem:**
When you trigger `lazy.reload_config()` in Qtile, `libqtile.confreader` clears its internal hook subscriptions and re-executes `~/.config/qtile/config.py` via `importlib.util.spec_from_file_location`. However, Python's `sys.modules` cache retains all previously imported submodules (`colors`, `settings`, `startup`, `groups`, `layouts`, `keys`, `bar`).

This causes two subtle bugs in multi-file Qtile configs:
1. **Edits to submodules are ignored** on `reload_config()` unless Qtile is completely restarted.
2. **All `@hook.subscribe` callbacks in submodules disappear** after `reload_config()`, because Qtile clears the hook registry before reloading `config.py`, and cached submodules never re-execute their `@hook.subscribe` decorators!

**The Solution:**
1. In `qtile/config.py`, already-loaded submodules are explicitly reloaded in **topological dependency order** (`colors` $\rightarrow$ `settings` $\rightarrow$ `startup` $\rightarrow$ `groups` $\rightarrow$ `layouts` $\rightarrow$ `keys` $\rightarrow$ `bar`) via `importlib.reload()`.
2. To prevent `importlib.reload(groups)` from wiping out live runtime state (such as which windows are currently sticky or in the dynamic scratchpad), `qtile/groups.py` preserves its `WindowStateTracker` instance across module reloads:
   ```python
   TRACKER: WindowStateTracker = globals().get("TRACKER") or WindowStateTracker()
   ```
   Because `importlib.reload()` re-executes the module in the existing module dictionary (`__dict__`), `TRACKER` survives across reloads while all `@hook.subscribe` decorators and updated rules are freshly registered.

---

### 3.2 Emulating i3's Default `workspace_layout tabbed`

In `i3wm`, setting `workspace_layout tabbed` displays a tab bar at the top of each workspace container and allows `Mod4+Left` / `Mod4+Right` to cycle through tabs.

In Qtile, this is achieved by combining three pieces:
1. **`layout.Max`** is set as the default workspace layout so the active window fills the workspace.
2. **`widget.TaskList`** in the status bar renders all windows in the current workspace as clickable tabs, using `parse_text=_format_tasklist_title` to prefix each tab with its FontAwesome icon (`` Code, `` Chrome, `` Firefox, `` PyCharm, etc.).
3. **`focus_direction()` in `keys.py`** checks whether the active layout is `"max"`. If so, `Mod4+Left` / `Mod4+Up` calls `prev_window()` and `Mod4+Right` / `Mod4+Down` calls `next_window()`, matching i3's tab cycling behavior while still performing spatial directional focus in split layouts (`Columns`, `Stack`).

---

### 3.3 Arbitrary Window Scratchpad vs. DropDown Terminal

In `i3wm`, `move scratchpad` (`Shift+F12`) can hide *any* window into the scratchpad, and `scratchpad show` (`F12` / `Mod4+Return`) toggles it back as a floating window. Qtile's built-in `ScratchPad` group only manages pre-configured `DropDown` processes.

`WindowStateTracker` in `qtile/groups.py` bridges both worlds:
* Pressing `Shift+F12` (`move_to_scratchpad`) records the focused window's ID and moves it to a hidden `_i3_scratchpad` group.
* Pressing `F12` or `Mod4+Return` (`toggle_scratchpad`) checks if any arbitrary window was stashed in `_i3_scratchpad` and toggles it onto the current workspace as a floating window; if none exists, it toggles the `xfce4-terminal` `DropDown` scratchpad.

---

### 3.4 Single-Shot vs. Persistent `KeyChord` Modes

In `i3wm`, every mode is persistent until `mode "default"` is triggered—which is why `mode-central-control.conf` and `mode-i3configger.conf` had to prepend `xdotool key Escape && ...` to every command.

In Qtile, `KeyChord` supports a `mode` boolean parameter:
* **`mode=False` (Single-Shot)**: Used for `Mod4+c` (`CENTRAL-CONTROL-PROGRAM`) and `Mod4+w` (`qtile-config`). Qtile displays the mode prompt in `widget.Chord`, waits for one keypress, executes the action, and automatically exits the mode—no `xdotool key Escape` hack required.
* **`mode=True` (Persistent)**: Used for `Mod4+r` (`resize / move`), allowing repeated `Left`/`Right`/`Up`/`Down` or `h`/`j`/`k`/`l` adjustments until `Escape` is pressed.

---

## 4. Dynamic Runtime Controls (`Mod4+w`)

Pressing `Mod4+w` enters the **Qtile Config & Theme Control** mode (`RuntimeState` persisted in `~/.config/qtile/state.json`):

| Key after `Mod4+w` | Action |
| :--- | :--- |
| `Left` / `Right` | Cycle between **Solarized Dark** and **Solarized Light** themes and reload Qtile. |
| `Up` / `Down` | Move status bar to **top** or **bottom** of all screens and reload Qtile. |
| `Shift+Up` / `Shift+Down` | Increase / decrease layout and bar font sizes by **±1pt** (clamped to `8pt..32pt`, with proportional bar height scaling). |
| `Shift+Right` / `Shift+Left` | Increase / decrease layout and bar font sizes by **±2pt**. |
| `0` | Reset font sizes to default (**14pt** layout / **15pt** bar). |
| `Return` / `r` | Reload Qtile configuration in place (`lazy.reload_config()`). |
| `c` | Full restart of Qtile (`lazy.restart()`). |
| `x` | Shut down / exit Qtile (`lazy.shutdown()`). |

---

## 5. Testing Without an X11 Session

The test suite in `tests/test_qtile_config.py` installs a lightweight stub of `libqtile` into `sys.modules` and replicates `libqtile.confreader.Config.load()`. It verifies:
1. All required Qtile symbols (`keys`, `groups`, `layouts`, `floating_layout`, `screens`, `mouse`, `widget_defaults`, `wmname`) load cleanly.
2. Simulating `qtile.reload_config()` (clearing the hook registry and re-executing `config.py`) re-registers all `@hook.subscribe` callbacks (`startup`, `setgroup`, `client_new`, `client_killed`) while preserving live `WindowStateTracker` state.
3. `RuntimeState` persistence for theme cycling, bar position switching, and font size clamping/resetting.
4. Window title icon regex matching and priority ordering (`ICON_TITLE_RULES` before `ICON_CLASS_RULES`).

# Qtile Configuration (Converted from i3wm)

This directory contains a modular [Qtile](https://qtile.org/) configuration converted from the `i3wm` + `i3configger` + `py3status` setup.

For full architectural details, design rationale, and lessons learned (such as handling `sys.modules` caching and hook registration during `qtile.reload_config()`), see **[docs/qtile.md](../docs/qtile.md)**.

## Installation

Symlink this `qtile` folder to `~/.config/qtile`:

```bash
ln -sfn "$(pwd)/qtile" ~/.config/qtile
```

Validate the configuration with Qtile:

```bash
qtile check
```

Run the automated unit tests:

```bash
python3 -m unittest discover -s tests -v
```

## Module Overview

| Qtile Module | i3wm Source | Description |
| :--- | :--- | :--- |
| `config.py` | `config` | Main Qtile entrypoint; reloads submodules in dependency order on `reload_config()` and exports Qtile settings. |
| `settings.py` | `0-basic-setup.conf`, `i3configger.json` | Modifiers, `pathlib.Path` constants, detached process helpers, and `RuntimeState` (`~/.config/qtile/state.json`) for theme, bar position, and font scaling. |
| `colors.py` | `0-basic-setup.conf`, `colors.0-dark.conf`, `colors.1-light.conf` | `ColorTheme` frozen dataclass and Solarized Dark/Light themes. |
| `startup.py` | `1-startup.conf` | `@hook.subscribe.startup` hook running `xset -dpms`, `dunst`, `unclutter`, `touchpad-settings.sh`, and `nitrogen --restore`. |
| `groups.py` | `0-basic-setup.conf`, `3-window-settings.conf` | `WorkspaceSpec` definitions (`1`–`10`), `TitleIconRule` formatting, floating rules, and reload-safe `WindowStateTracker` for sticky windows (`Control+F12`) and arbitrary window scratchpad (`Shift+F12` / `F12` / `Mod4+Return`). |
| `layouts.py` | `0-basic-setup.conf` | `Max` (default tabbed equivalent), `Columns` (split), `Stack` (stacking), `TreeTab`, and `Floating` (`3px` border). |
| `keys.py` | `control-main-key-bindings.conf`, `mode-*.conf` | Navigation, window manipulation, media keys, Rofi launchers, and `KeyChord` modes (`Mod4+c`, `Mod4+w`, `Mod4+r`). |
| `bar.py` | `i3bar.simple.conf`, `i3bar.full.conf`, `py3status/` | `SystemStatusPoller` (`/proc` & `/sys` via `pathlib.Path`) and built-in Qtile bar widgets (`GroupBox`, `Chord`, `TaskList`, `sysdata`, `wifi`, `uname`, `diskdata`, `online_status`, `volume_status`, `battery_level`, `Clock`, `Systray`). |
