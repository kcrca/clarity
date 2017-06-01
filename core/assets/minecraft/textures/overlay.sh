#!/bin/sh

if [ x"$1" == x"-rm" ]; then
    rm_only=yes
    shift
fi

typeset -a dirs
dirs=( "$@" )
if [ ${#dirs} -eq 0 ]; then
    dirs=( . )
fi

find "${dirs[@]}" -name '*_diff.gif' -delete
[ -z "$rm_only" ] || exit 0

html=/tmp/overaly.html
cp /dev/null $html
skipped=""

for new in $(find "${dirs[@]}" -name '*.png'); do
    echo $new
    new="$(cd "$(dirname $new)" ; pwd)/$(basename $new)"
    old="${new/core/default_resourcepack}"
    base=$(dirname $new)/$(basename $new .png)
    short_name=$(echo $base | sed -e 's,.*minecraft/,,')
    if [ -f $old ]; then
	caption="-background White label:$short_name -gravity Center -append"
	# scale on width since height might vary for animation
	new_width=$(identify -format '%w\n' $new)
	old_width=$(identify -format '%w\n' $old)
	max_width=$(echo $new_width\\n$old_width| sort -nr | head -1)
	new_scale=$(echo "100 * $max_width / $new_width" | bc)
	old_scale=$(echo "100 * $max_width / $old_width" | bc)
	new_img="( $new -resize $new_scale% )"
	old_img="( $old -resize $old_scale% )"
	img=${base}_diff.gif
	convert -delay 100 \
	    \( $new_img $caption \) \
	    \( $new_img $old_img -gravity northwest -compose Overlay -composite $caption \) \
	    \( $old_img $caption \) \
	    \( $old_img $new_img -gravity northwest -compose Overlay -composite $caption \) \
	    -loop 0 -border 1 $img
	cat <<EOF >>$html
<img src="$img" alt="$short_name" style="margin: 10px"/>
EOF
    else
        skipped="$skipped<li>$short_name"
    fi
done

if [ x"$skipped" != x"" ]; then
    cat <<EOF >>$html
<p>Skipped:<ul>$skipped</ul>
EOF
fi

run open $html
