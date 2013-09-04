#!/bin/bash

$HOME/.i3/bin/create_lockscreen.sh
i3lock -i /tmp/lockscreen.png &
sudo pm-suspend