#!/bin/sh
set -e

bin=`dirname $0`

remove_only=0
if [ x"$1" == x"-rm" ]; then
    remove_only=1
    shift
fi

cd $bin/..
top=$PWD
d=$top/default_resourcepack
[ -d $d ] || (echo "No default pack: " $d && exit 1) 1>&2

find . -name .[dc] -type l -delete
if [ "$remove_only" == "1" ]; then
    exit 0
fi

(( $remove_only )) && exit 0

c=$top/core
cd $c
for f in `find . -type d`; do
    o=$d/$f
    [ -d $o ] && ln -s $o $f/.d
done

for d in $top/*.repack/override; do
    cd $d
    for f in `find . -type d`; do
        o=$c/$f
        [ -d $o ] && ln -s $o $f/.c
    done
done

c=$top/core/assets/minecraft
for d in $top/core/assets/*; do
    if [[ -d $d && ! $d =~ 'minecraft' ]]; then
	cd $d
	for f in `find . -type d`; do
	    o=$c/$f
	    [ -d $o ] && ln -s $o $f/.c
	done
    fi
done
