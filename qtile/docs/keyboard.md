# Keyboard

* Key names are X11 keysyms in `config.d/keys.py` (German layout: `numbersign`, `udiaeresis`, `asciicircum`), as in i3.
  The layout itself is not set by the config, it is whatever X11 uses (`setxkbmap de`), use `xev` to look up names.
  Qtile can also set it with `widget.KeyboardLayout`/`setxkbmap` in `startup.py` (not done).
* `MOD` is `mod4`, `ALT` is `mod1` (`config.d/settings.py`).
* List bindings: `bin/qtile-show-bindings.sh`.
* Every `Key` has a `desc` which is what `display_kb` prints.
