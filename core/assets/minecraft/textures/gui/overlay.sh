#!/bin/sh

dirs=( "$@" )
if [ ${#dirs} -eq 0 ]; then
    dirs=( . )
fi

find $dirs -name '*_diff.png' -print0 | xargs -0 rm

for new in `find $dirs -name '*.png'`; do
    new="$(cd "`dirname $new`" ; pwd)/$(basename $new)"
    old="${new/core/default_resourcepack}"
    if [ -f $old ]; then
        echo $new
        base=`dirname $new`/`basename $new .png`
	caption="-background White label:"$base" -gravity Center -append"
	convert -delay 100 \
	    \( $new $caption \) \
	    \( $new $old -gravity center -compose Overlay -composite $caption \) \
	    \( $old $caption \) \
	    \( $old $new -gravity center -compose Overlay -composite $caption \) \
	    -loop 0 ${base}_diff.gif
    else
        echo ... skipping $new
    fi
done
