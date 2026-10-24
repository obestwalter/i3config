#!/bin/bash
# Replacement for i3-show-bindings.sh. Qtile knows its bindings itself:
# `display_kb` lists the key bindings of the running Qtile (including KeyChord modes).

qtile cmd-obj -o root -f display_kb
