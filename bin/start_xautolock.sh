#!/bin/bash -

set -o nounset                              # Treat unset variables as an error
xautolock -time 5 -corners +--- -cornerdelay 5 -cornerredelay 60 -notifier 'notify-send --expire-time 2 "about to lock the screen ..."' -notify 3 -locker "i3lock -i ~/chill/wallpapers/cassini_derelict.png" &

#xautolock -time 5 -notifier 'echo "screen     lock  " | dzen2 -p 10 -y 512 -bg "#770000"' -notify 3 -locker "i3lock -i ~/chill/wallpapers/cassini_derelict.png" &
