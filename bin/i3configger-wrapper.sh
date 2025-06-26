#!/bin/bash

I3CONFIGGER="$HOME/_sys/bin/i3configger"
PID=$(pgrep i3configger)

if [ "$PID" == "" ]; then
  i3configger --watch -v &
  PID=$(pgrep i3configger)
  notify-send -a "$I3CONFIGGER" "started @$PID"
fi

if ! $I3CONFIGGER "$1"; then
  notify-send --urgency=critical -a "$I3CONFIGGER" "failed: $1"
else
  notify-send --urgency=low -a "$I3CONFIGGER" "done: $1"
fi
