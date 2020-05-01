#!/bin/bash

PID=$(pgrep screenkey)

if [ "$PID" != "" ]; then
  kill "$PID"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'screenkey killed'
else
  screenkey &
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'screenkey started'
fi
