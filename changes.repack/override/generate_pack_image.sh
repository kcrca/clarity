#!/bin/sh

# Relies on ImageMagick "convert" commmand

script_dir=$(dirname $0)

#convert \
#    -size 512x512 \
#    -define gradient:vector=0,256,128,256 \
#    gradient:'srgb(47,255,0)-srgb(79,113,31)' \
#    -define gradient:vector=128,256,384,256 \
#    gradient:'srgb(79,113,31)-srgb(172,92,49)' \
#    pack.png

# Every size is scaled by 8 (note third arg of Arc)

./multigradient.sh -w 512 -h 512 -s "
    rgb(47,255,0)
    rgb(79,163,31) 20
    rgb(79,163,31) 70
    rgb(246,231,66) 80
    rgb(231,101,1) 90
    rgb(175,23,28)
    " \
	-t linear -d to-right pack.png

#convert pack.png -fill 'rgb(237,231,184)' -draw 'rectangle 16,16 496,496' pack.png
