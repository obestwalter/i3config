#!/bin/bash

notify-send --expire-time 100 "Locking screen ..."
$HOME/.i3/bin/create_lockscreen.sh
i3lock -i /tmp/lockscreen.png
