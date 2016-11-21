#!/bin/sh
rm -f *.gif
top=../../..
set -e
for c in clarity connectivity continuity; do
    uc=$(echo "$(tr a-z A-Z <<< ${c:0:1})${c:1}")
    convert -composite \
	${c}_example.png \
	$top/site/${c}_thumb.png -geometry +10+10 \
	-fill white -font Verdana -pointsize 24 -gravity SouthWest -annotate +84+6 ${uc} \
	${c}_frame.gif
done
convert -delay 100 *.gif -loop 0 ../../comparison_anim.gif
rm -f *.gif
