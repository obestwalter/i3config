#!/bin/bash
#
# Changes the wallpaper hourly and displays a projection of the earth with
# a semi-realistic rendered sunglight mapping.
#
# This script will download hourly the "World Sunlight Map" by die.net.
# You can choose the world_sunlight_wallpaper.jpg picture as background image for your Desktop.
# Gnome recognizes file changes and updates the background accordingly.
#
# See:
# - https://www.die.net/earth/rectangular.html
# - https://www.die.net/earth/how.html
#
# Via: http://www.webupd8.org/2009/09/real-time-earth-wallpaper-for-linux.html
# and: https://gist.github.com/thet/f915cf4a44364f95d48e2cc8ece3d041

cd $HOME/Pictures/wallpapers/single_screen/
while [ 1 ]; do
    COUNTER=0
    while [ $COUNTER -lt 60 ]; do
        wget http://images.opentopia.com/sunlight/world_sunlight_map_rectangular.jpg -O world.jpg
        temp=$(stat -c%s world.jpg)
        if [[ $temp > 1000 ]]; then
            #mv world.jpg tmp/world_sunlight_wallpaper-$(date +%F-%T).jpg
            mv world.jpg world_sunlight_wallpaper.jpg
            echo "updated world wallpaper"
            break
        fi
        sleep 5
        let COUNTER=COUNTER+1
    done
    sleep 3600
done
