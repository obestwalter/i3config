#!/bin/bash
# screenkey is X11 only, wshowkeys is the wayland equivalent (needs to be setuid root or in the input group)

PID=$(pgrep wshowkeys)

if [ "$PID" != "" ]; then
  kill "$PID"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'wshowkeys killed'
else
  wshowkeys -a bottom -m 20 &
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'wshowkeys started'
fi
