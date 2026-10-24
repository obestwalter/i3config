# My [Qtile](https://qtile.org/) config

Port of the i3 config in the parent folder with the same structure, aiming to replace it later.
Qtile is configured in Python, so the partials in `config.d/` are Python modules instead of i3 config snippets.

| i3 (parent folder)            | qtile (this folder)                                                   |
|-------------------------------|-----------------------------------------------------------------------|
| `config` (generated)          | `config.py` (entrypoint, imports `config.d/*`)                        |
| `config.d/*.conf`             | `config.d/*.py` (see mapping below)                                   |
| `i3configger`                 | not needed, theme/bar/font switching is native (`Mod4+w`, `state.json`) |
| `bin/`                        | `bin/` (shared X11 scripts + qtile specific ones)                     |
| `configs-other/`              | `configs-other/`                                                      |
| `py3status/`, `i3bar.*.conf`  | `config.d/bar.py` (built-in widgets, no py3status)                    |
| `docs/`                       | `docs/`                                                               |
| `install-dependencies.sh`     | `install-dependencies.sh`                                             |
| `mkdocs.yml`                  | `mkdocs.yml`                                                          |

| i3 `config.d`                                           | Qtile `config.d`                  |
|---------------------------------------------------------|-----------------------------------|
| `0-basic-setup.conf`, `i3configger.json`                | `settings.py`, `colors.py`, `layouts.py`, `groups.py` (workspaces) |
| `colors.0-dark.conf`, `colors.1-light.conf`             | `colors.py`                       |
| `1-startup.conf`                                        | `startup.py`                      |
| `3-window-settings.conf`                                | `groups.py` (title icons, floating rules) |
| `control-main-key-bindings.conf`, `mode-*.conf`         | `keys.py`                         |
| `i3bar.*.conf`, `py3status/`                            | `bar.py`                          |

## Install

```sh
./install-dependencies.sh
ln -sfn "$PWD" ~/.config/qtile     # or copy
qtile check                        # validate the config
python3 -m unittest discover -s . -v   # tests, no X11/libqtile needed
```

Docs: [docs/index.md](docs/index.md) (architecture and lessons learned in [docs/qtile.md](docs/qtile.md),
what changed in [docs/migration.md](docs/migration.md), known problems in
[docs/findings-and-risks.md](docs/findings-and-risks.md)).
