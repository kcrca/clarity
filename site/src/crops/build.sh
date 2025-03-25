#!/bin/sh
scale="100%"
magick -dispose previous -delay 20 crops_0.png crops_1.png crops_2.png crops_3.png crops_4.png crops_5.png crops_6.png -delay 40 crops_7.png -delay 70 crops_8.png -loop 0 -layers optimize ../../crops.gif
