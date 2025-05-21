#!/bin/bash

grep "^bindsym" ~/.i3/config \
    | sed 's/-\(-\w\+\)\+//g;s/Mod4/Win/g;s/Mod1/Alt/g;s/exec //;s/bindsym //;s/^\s\+//;s/^\([^ ]\+\) \(.\+\)$/\2: \1/;s/^\s\+//' \
    | tr -s ' ' \

#find config.d/ -maxdepth 1 -not -name "mode*" -type f -print0 | xargs -0 grep "^bindsym" | sort | awk '{$1=""; print $0}'