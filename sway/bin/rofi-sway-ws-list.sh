#!/bin/bash -
# Sway equivalent of rofi-i3-ws-list.sh (switch to selected workspace)
# Depends on: swaymsg, jq, rofi (wayland capable, e.g. rofi-wayland or rofi >= 2.0)
wslist () {
    swaymsg -t get_workspaces -r | jq -r '.[].name' | sort -V
}

case $1 in
    [0-9]*)
        swaymsg workspace number "$1" > /dev/null
        ;;
    ?*)
        swaymsg workspace "$1" > /dev/null
        ;;
    *)
        wslist
        ;;
esac
