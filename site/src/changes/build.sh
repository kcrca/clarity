#!/bin/sh
cd $(dirname $0)
set -e
declare -a files
files=()
for s in spring summer fall winter; do
    c=$(echo *_${s}.png)
    uc=$(echo "$(tr a-z A-Z <<< ${s:0:1})${s:1}")
    g="${s}_frame.gif"
    magick \
	$c \
	-fill white -font Verdana -pointsize 24 -gravity SouthWest -annotate +6+6 ${uc} \
	$g
    files=("${files[@]}" "$g")
done
magick -delay 210 "${files[@]}" -loop 0 -resize 750x483 ../../changes.gif
rm -f *.gif
