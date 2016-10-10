#!/bin/sh
scale="50%"
convert -delay 10 crops_0.png crops_1.png crops_2.png crops_3.png crops_4.png crops_5.png crops_6.png -delay 60 crops_7.png -scale "$scale" -loop 0 ../../crops_anim.gif
