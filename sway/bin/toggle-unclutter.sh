#!/bin/bash
# unclutter is X11 only, sway hides the cursor via "seat * hide_cursor <ms>" (0 = never hide)

STATE_FILE=/tmp/sway-hide-cursor

if [ -e "$STATE_FILE" ]; then
  swaymsg seat '*' hide_cursor 0 > /dev/null
  rm "$STATE_FILE"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'hide_cursor off'
else
  swaymsg seat '*' hide_cursor 1000 > /dev/null
  touch "$STATE_FILE"
  notify-send -a 'CENTRAL-CONTROL-PROGRAM' 'hide_cursor on'
fi
