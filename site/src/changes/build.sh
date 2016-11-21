#!/bin/sh
convert -delay 200 *.png -loop 0 ../../changes_anim.gif
set -e
for c in *.png; do
    n=$(basename ${c/??_/} .png)
    uc=$(echo "$(tr a-z A-Z <<< ${n:0:1})${n:1}")
    convert \
	$c \
	-fill white -font Verdana -pointsize 24 -gravity SouthWest -annotate +6+6 ${uc} \
	${n}_frame.gif
done
convert -delay 210 *.gif -loop 0 ../../changes_anim.gif
rm -f *.gif
