#!/bin/sh

bin=`dirname $0`
cd $bin/..
top=$PWD
d=$top/default_resourcepack
[ -d $d ] || (echo "No default pack: " $d && exit 1) 1>&2

find . -name .[dc] -type l -delete

c=$top/core
cd $c
for f in `find . -type d`; do
    o=$d/$f
    [ -d $o ] && echo ln -s $o $f/.d && ln -s $o $f/.d
done

for d in $top/*.repack/override; do
    echo cd $d
    cd $d
    for f in `find . -type d`; do
        o=$c/$f
        [ -d $o ] && echo ln -s $o $f/.c && ln -s $o $f/.c
    done
done

c=$top/core/assets/minecraft
for d in $top/core/assets/*; do
    if [[ -d $d && ! $d =~ 'minecraft' ]]; then
	echo cd $d
	cd $d
	for f in `find . -type d`; do
	    o=$c/$f
	    [ -d $o ] && echo ln -s $o $f/.c && ln -s $o $f/.c
	done
    fi
done