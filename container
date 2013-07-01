#!/bin/zsh -e
cd /tmp
rm -rf container
mkdir container
cd container

set -x

bg=lightGrey

((slot_size=18))

convert -size 16x16 xc:darkGrey -bordercolor $bg -border 1 slot.png
convert -size $((9 * $slot_size))x$((1 * $slot_size)) tile:slot.png row.png

convert -size $((9 * $slot_size))x$((6 * $slot_size)) tile:row.png upper.png
convert -size $((9 * $slot_size))x$((3 * $slot_size)) tile:row.png mid.png

convert -size 176x222 xc:$bg \
	upper.png -geometry +7+17  -composite \
	mid.png   -geometry +7+139 -composite \
	row.png   -geometry +7+197 -composite \
	container-ui.png

convert -size 256x256 xc:none \
	container-ui.png -composite \
	container.png

open *.png
