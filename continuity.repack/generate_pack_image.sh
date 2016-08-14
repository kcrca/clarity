#!/bin/sh

# Relies on ImageMagick "convert" commmand

convert -font OratorStd -pointsize 36 \
  -background 'rgb(237,231,184)' label:' Continuity ' -virtual-pixel background -distort Arc '360 60' \
  -bordercolor 'rgb(237,231,184)' -border 2 override/pack.png
