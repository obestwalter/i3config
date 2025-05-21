#!/bin/bash

# configure via "screenkey --show-settings"

PID=$(pgrep screenkey)

if [ "$PID" != "" ]; then
  kill "$PID"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'screenkey killed'
else
  screenkey --mods-only --mods-mode tux &
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'screenkey started'
fi
