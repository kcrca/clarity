#!/bin/sh
scale="50%"
convert -delay 120 ores_in_lava*.png -scale "$scale" -resize 750x483 -loop 0 ../../ores_in_lava_anim.gif
