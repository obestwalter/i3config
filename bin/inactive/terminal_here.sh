#!/bin/bash
ID=$(xprop -root | awk '/_NET_ACTIVE_WINDOW\(WINDOW\)/{print $NF}')
NAME=$(xprop -id $ID | awk '/WM_CLASS\(STRING\)/{print $NF}')
PID=($(xprop -id $ID | awk '/_NET_WM_PID\(CARDINAL\)/{print $NF}'))
CPID=($(ps --ppid $PID |awk '/^[0-9]/ {print $1}' ))
while [ -n "$CPID" ]
do
    CPID=$(ps --ppid $PID |awk '/^[0-9]/ {print $1}')
    if [ -e "/proc/$CPID/cwd" ]
    then
    PID=$CPID
    fi
done
if [ -e "/proc/$PID/cwd" ]
then
    urxvt -cd $(readlink /proc/$PID/cwd) &
    echo "cd $PID">~/t
else
    echo "no cd $PID">~/t
    urxvt
fi
