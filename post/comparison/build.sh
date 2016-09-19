#!/bin/sh
rm -f *.gif
set -e
for c in clarity connectivity continuity; do
    convert -composite \
	${c}_example.png \
	../../${c}.repack/override/pack_thumb.png -geometry +10+10 \
	-fill white -font Verdana -pointsize 24 -gravity SouthWest -annotate +84+6 ${c} \
	${c}_frame.gif
done
convert -delay 100 *.gif -loop 0 comparision.gif
