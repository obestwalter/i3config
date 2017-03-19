#!/bin/bash

if synclient -l | grep "TouchpadOff .*=.*0" ; then
    synclient TouchpadOff=1 ;
    xdotool mousemove 1500 1500
else
    synclient TouchpadOff=0 ;
fi
