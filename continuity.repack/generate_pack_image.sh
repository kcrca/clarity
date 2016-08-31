#!/bin/sh

# Relies on ImageMagick "convert" commmand

convert \
    -pointsize 110 \
    -background 'rgb(237,231,184)' -virtual-pixel HorizontalTile -distort Arc '360 90 255' \
    label:' Continuity ' \
    override/pack.png
