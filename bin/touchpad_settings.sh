#!/bin/bash

# xinput --list
PROP="VEN_0488:00 0488:104B Touchpad"
#xinput list-props "$PROP"

xinput set-prop "$PROP" "libinput Tapping Enabled" 1
xinput set-prop "$PROP" "libinput Tapping Drag Lock Enabled"	1
