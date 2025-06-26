#!/bin/bash

I3CONFIGGER="$HOME/_sys/bin/i3configger"
PID=$(pgrep i3configger)

if [ "$PID" == "" ]; then
  i3configger --watch -v &
  PID=$(pgrep i3configger)
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' "i3configger started @$PID"
fi

if ! $I3CONFIGGER "$1"; then
  notify-send --urgency=critical -a 'CENTRAL-CONTROL-PROGRAM' "$I3CONFIGGER $1 failed"
else
  notify-send --urgency=low -a 'CENTRAL-CONTROL-PROGRAM' "$I3CONFIGGER $1"
fi
