#!/bin/bash
# xinput is X11 only, sway can enable/disable input devices itself

swaymsg input type:touchpad events toggle enabled disabled > /dev/null
STATE=$(swaymsg -t get_inputs -r | jq -r '[.[] | select(.type == "touchpad")][0].libinput.send_events')

if [ "$STATE" = "enabled" ]; then
    notify-send -t 1000 -a 'CENTRAL-CONTROL-PROGRAM' 'touchpad enabled'
else
    notify-send -t 1000 -a 'CENTRAL-CONTROL-PROGRAM' 'touchpad disabled'
fi
