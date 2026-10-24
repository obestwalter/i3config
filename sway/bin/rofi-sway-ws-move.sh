#!/bin/bash -
# Sway equivalent of rofi-i3-ws-move.sh (move focused window to selected workspace)
wslist () {
    swaymsg -t get_workspaces -r | jq -r '.[].name' | sort -V
}

case $1 in
    [0-9]*)
        swaymsg move container to workspace number "$1" > /dev/null
        ;;
    ?*)
        swaymsg move container to workspace "$1" > /dev/null
        ;;
    *)
        wslist
        ;;
esac
