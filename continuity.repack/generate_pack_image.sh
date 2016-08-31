#!/bin/sh

# Relies on ImageMagick "convert" commmand

convert \
    -font Verdana -pointsize 110 \
    -define distort:viewport=512x512-256-256 \
    -background 'rgb(237,231,184)' -virtual-pixel HorizontalTile -distort Arc '415 90 280' \
    label:' continuity ' \
    override/pack.png
