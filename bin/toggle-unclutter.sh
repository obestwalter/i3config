#!/bin/bash

PID=$(pgrep unclutter)

if [ "$PID" != "" ]; then
  kill "$PID"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'unclutter killed'
else
  unclutter --timeout 1 --ignore-scrolling &
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'unclutter started'
fi
