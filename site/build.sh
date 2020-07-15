#!/bin/sh
cd $(dirname $0)
for f in src/*/; do
    name=$(dirname $f/.)
    out=$(basename $name)
    if test ! -f $out.gif || find $name -newer $out.gif | grep -q . > /dev/null ; then
	case $out in
	    download)
		echo - convert -delay 200 $name/\*.png -loop 0 -resize 32x32 $out.gif
		convert -delay 200 $name/*.png -loop 0 -scale 32x32 $out.gif
		;;
	    *)
		echo - convert -delay 200 $name/\*.png -loop 0 -resize 750x483 $out.gif
		convert -delay 200 $name/*.png -loop 0 -resize 750x483 $out.gif
		;;
	esac
    fi
done
