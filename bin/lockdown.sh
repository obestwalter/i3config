#!/bin/bash

# set -xe

notify-send -a CENTRAL-CONTROL-PROGRAM -t 2500 --urgency critical 'SYSTEM LOCKDOWN INITIATED!'

tidy-up() {
  rm /tmp/*lockscreen*.png
}

trap tidy-up HUP INT TERM

scrot /tmp/lockscreen.png

convert -blur 0x6 /tmp/lockscreen.png /tmp/lockscreen.png
convert -composite /tmp/lockscreen.png "$(dirname $0)"/viking-guard.png /tmp/lockscreen.png
i3lock -i /tmp/lockscreen.png
tidy-up
