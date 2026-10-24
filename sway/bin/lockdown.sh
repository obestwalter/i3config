#!/bin/bash
# pixelated lock screen. Depends on: grim, imagemagick, swaylock

inpath=/tmp/screenshot.png
outpath=/tmp/lockscreen.png
grim ${inpath}

convert -scale 10% -scale 1000% ${inpath} ${outpath}

rm $inpath

swaylock -f -i $outpath
