#!/bin/bash

# set -x

declare -i ID
ID=$(xinput list | grep -Eio '(touchpad|glidepoint)\s*id\=[0-9]{1,2}' | grep -Eo '[0-9]{1,2}')
declare -i STATE
STATE=$(xinput list-props "$ID"|grep 'Device Enabled'|awk '{print $4}')
#UNCLUTTER_PID=$(pgrep unclutter)
if [ "$STATE" -eq 1 ]; then
    xinput disable "$ID"
    notify-send -t 1000 -a 'CENTRAL-CONTROL-PROGRAM' 'touchpad disabled'
#    if [ "$UNCLUTTER_PID" = "" ]; then
#      xdotool mousemove 5000 5000
#    fi
      # send outside of viewport => pops up again middle/lower third of screen then
      xdotool mousemove 5000 5000
else
    xinput enable "$ID"
    notify-send -t 1000 -a 'CENTRAL-CONTROL-PROGRAM' 'touchpad enabled'
#    if [ "$UNCLUTTER_PID" = "" ]; then
#      xdotool mousemove 1000 500
#    fi
fi
