#!/bin/bash - 
#
#vim:foldmethod=marker commentstring=\ ##%s
#===============================================================================
#
#          FILE:  start_xautolock.sh
# 
#         USAGE:  ./start_xautolock.sh 
# 
#   DESCRIPTION:  starts xautolock
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Matthias Ruf (mruf), matthias.ruf@avira.com
#  ORGANIZATION: Avira Operations GmbH & Co. KG
#       CREATED: 2012-04-17 10:54:13
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
xautolock -time 3 -notifier 'echo "screen     lock  " | dzen2 -p 2 -y 512 -bg "#770000"' -notify 3 -locker "i3lock -i /home/obestwalter/Documents/Pictures/wallpapers/cassini_dereilct.png" &

