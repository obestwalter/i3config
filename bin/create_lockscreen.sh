#!/bin/bash

inpath=/tmp/screenshot.png
outpath=/tmp/lockscreen.png
scrot ${inpath}
#convert -scale 25% -scale 400% ${inpath} ${outpath}
#convert -flop ${inpath} ${outpath}
#convert -negate ${inpath} ${outpath}
#convert -motion-blur 20x20 ${inpath} ${outpath}
convert -flop -fill orange -tint 100 ${inpath} ${outpath}
#convert -wave 2x3 ${inpath} ${outpath}
#feh ${outpath}
