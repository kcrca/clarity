#!/bin/sh
pwd
rm -f *.gif
top=../../..
set -e
for c in clarity continuity connectivity vanilla; do
    uc=$(echo "$(tr a-z A-Z <<< ${c:0:1})${c:1}")
    magick ${c}_example.png $top/site/${c}_thumb.png \
	-geometry +10+10 -fill white -font Verdana -pointsize 24 -gravity SouthWest -annotate +84+6 ${uc} -composite  \
	${c}_frame.gif
done
magick -delay 200 *.gif -loop 0 ../../comparison.gif
rm -f *.gif
