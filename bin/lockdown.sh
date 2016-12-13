#!/bin/bash

inpath=/tmp/screenshot.png
outpath=/tmp/lockscreen.png
scrot ${inpath}

#convert -scale 10% -scale 1000% ${inpath} ${outpath}
#convert -negate ${inpath} ${outpath}
#convert -motion-blur 20x20 ${inpath} ${outpath}
convert -motion-blur 25x25 -flop -fill orange -tint 100 ${inpath} ${outpath}
#convert -wave 2x3 ${inpath} ${outpath}

rm $inpath

i3lock -i $outpath
#feh ${outpath}
