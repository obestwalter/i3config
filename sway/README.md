# My [sway](https://swaywm.org/) config

Drop-in successor of the i3 config in the parent folder, same structure:

| i3 (parent folder)            | sway (this folder)                                   |
|-------------------------------|------------------------------------------------------|
| `config` (generated)          | `config` (hand written, `include`s `config.d/*`)     |
| `config.d/`                   | `config.d/` (same partials, ported)                  |
| `i3configger`                 | not needed, sway has `include`; `bin/sway-colors.sh` |
| `bin/`                        | `bin/` (Wayland replacements)                        |
| `configs-other/`              | `configs-other/`                                     |
| `py3status/`, `i3bar.*.conf`  | `py3status/`, `i3bar.*.conf` (work with swaybar)     |
| `docs/`                       | `docs/`                                              |

## Install

```sh
./install-dependencies.sh
ln -s "$PWD" ~/.config/sway     # or copy
sway -C                         # validate the config
```

The config refers to `~/.config/sway` (`$swayHome` in `config.d/0-basic-setup.conf`).

See [docs/migration.md](docs/migration.md) for what changed and why, and
[docs/windows.md](docs/windows.md) for finding window properties.

When this is stable the parent folder's i3 files can be replaced by the content of this folder.
