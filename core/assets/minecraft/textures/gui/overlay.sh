#!/bin/sh

dirs=( "$@" )
if [ ${#dirs} -eq 0 ]; then
    dirs=( . )
fi

find $dirs -name '*_diff.png' -print0 | xargs -0 rm

for new in $(find $dirs -name '*.png'); do
    new="$(cd "$(dirname $new)" ; pwd)/$(basename $new)"
    old="${new/core/default_resourcepack}"
    if [ -f $old ]; then
	base=$(dirname $new)/$(basename $new .png)
	short_name=$(echo $base | sed -e 's,.*minecraft/,,')
	caption="-background White label:'$short_name' -gravity Center -append"
        echo $short_name
	# scale on width since height might vary for animation
	new_width=$(identify -format '%w\n' $new)
	old_width=$(identify -format '%w\n' $old)
	max_width=$(echo $new_width\\n$old_width| sort -nr | head -1)
	new_scale=$(echo "100 * $max_width / $new_width" | bc)
	old_scale=$(echo "100 * $max_width / $old_width" | bc)
	new_img="( $new -resize $new_scale% )"
	old_img="( $old -resize $old_scale% )"
	convert -delay 100 \
	    \( $new_img $caption \) \
	    \( $new_img $old_img -gravity northwest -compose Overlay -composite $caption \) \
	    \( $old_img $caption \) \
	    \( $old_img $new_img -gravity northwest -compose Overlay -composite $caption \) \
	    -loop 0 -border 1 ${base}_diff.gif
    else
        echo ... skipping $new
    fi
done
