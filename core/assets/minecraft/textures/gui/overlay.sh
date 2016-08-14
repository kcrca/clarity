#!/bin/sh

interact=0
if [ x "$1" = x"-i" ]; then
    interact=1
    shift
fi

dirs=( "$@" )
if [ ${#dirs} -eq 0 ]; then
    dirs=( . )
fi

find $dirs -name '*_[on][no].png' | xargs rm

for new in `find $dirs -name '*.png'`; do
    new="$(cd"`dirname$new`";pwd)/$(basename$new)"
    old="${new/core/default_resourcepack}"
    if [ -f $old ]; then
        echo $new
        base=`dirname $new`/`basename $new .png`
        stop=0
        while [ $stop -eq 0 ]; do
            stop=1
            convert $new $old -gravity center -compose Overlay -composite ${base}_no.png
            convert $old $new -gravity center -compose Overlay -composite ${base}_on.png
            if [ $interact -ne 0 ]; then
                cp $new ${base}_nn.png
                cp $old ${base}_oo.png
                open -Wn -a /Applications/Preview.app ${base}_[no][on].png
                read -p "Edit? [yN] " edit
                case "$edit" in
                    [Yy]*)
                        open -Wn -a /Applications/Pixelmator.app $new $old
                        stop=1
                    ;;
                    *)
                        rm ${base}_[no][on].png
                    ;;
                esac
            fi
        done
    else
        echo ... skipping $new
    fi
done
