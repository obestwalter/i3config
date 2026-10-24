#!/bin/bash
# Replacement for i3-show-bindings.sh, reads all partials (sway has no single generated config)

cat ~/.config/sway/config.d/*.conf \
    | grep "^bindsym" \
    | sed 's/-\(-\w\+\)\+//g;s/\$win/Win/g;s/\$alt/Alt/g;s/exec //;s/bindsym //;s/^\s\+//;s/^\([^ ]\+\) \(.\+\)$/\2: \1/;s/^\s\+//' \
    | tr -s ' '
