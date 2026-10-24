#!/bin/bash
# Replaces i3configger "select-next/previous colors": switch the colors.conf symlink and reload sway.
# usage: sway-colors.sh next|prev

cd "$(dirname "$(readlink -f "$0")")/../config.d" || exit 1
schemes=(colors.[0-9]*.conf)
current=$(basename "$(readlink colors.conf)")

idx=0
for i in "${!schemes[@]}"; do
    [ "${schemes[$i]}" = "$current" ] && idx=$i
done

n=${#schemes[@]}
case $1 in
    next) idx=$(( (idx + 1) % n )) ;;
    prev) idx=$(( (idx + n - 1) % n )) ;;
    *) echo "usage: $(basename "$0") next|prev" >&2; exit 1 ;;
esac

ln -sf "${schemes[$idx]}" colors.conf
if swaymsg reload > /dev/null; then
    notify-send --urgency=low -a 'sway' "colors: ${schemes[$idx]}"
else
    notify-send --urgency=critical -a 'sway' "failed: ${schemes[$idx]}"
fi
