# Window properties

Replaces `i3-xprop.sh`.

```sh
bin/qtile-window-info.sh           # click on a window (X11, needs xprop)
bin/qtile-window-info.sh focused   # focused window via `qtile cmd-obj -o window -f info`
```

Output ends with a ready to use rule:

```
Match(wm_class="Code", wm_instance_class="code", title="main.py - proj - Visual Studio Code")
```

| i3 criteria | Qtile `Match` |
|-------------|---------------|
| `class`     | `wm_class`    |
| `instance`  | `wm_instance_class` |
| `title`     | `title` (regex allowed via `re.compile`) |
| `window_role` | `role`      |

Use them in `config.d/groups.py` (`ICON_CLASS_RULES` matches the class names directly as regex, `FORCE_TILE_MATCHES`
holds `Match` objects for `floating disable`).

Interactive inspection in a running Qtile: `qtile shell` → `cd windows`, `ls`, `window.info()`.
