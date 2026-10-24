# Window properties

Replaces `i3-xprop.sh`. Native wayland windows have an `app_id`, XWayland windows have `class`
and `instance` (`shell` is `xwayland`). Titles work for both.

```sh
bin/sway-window-info.sh          # click on a window (needs slurp)
bin/sway-window-info.sh focused  # focused window, e.g. sleep 3; ...
bin/sway-window-info.sh all      # everything
```

Output (last line is a ready to use criteria block):

```
id=42
app_id="firefox"
title="Sway - Mozilla Firefox"
shell=xdg_shell
[app_id="firefox" title="Sway - Mozilla Firefox"]
```

Raw access: `swaymsg -t get_tree | jq '.. | select(.focused? == true)'`

## Rules

Put both criteria into `config.d/3-window-settings.conf` so the rule works however the app is started:

```
for_window [app_id="firefox"] title_format "..."
for_window [class="(?i)firefox"] title_format "..."
```

Test a criteria without a rule: `swaymsg '[app_id="firefox"] mark test'` (`success: true` if it matched).

Differences to i3:

* `window_role` is not available for native windows.
* `instance` only exists for XWayland windows.
* `assign` works with both `app_id` and `class`.
