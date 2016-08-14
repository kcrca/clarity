#!/bin/sh

top=`dirname $0`
cd $top
top=$PWD
d=$top/default_resourcepack
[ -d $d ] || (echo "No default pack: " $d && exit 1) 1 > &2

c=$top/core
cd $c
find . -name .d -type l -delete
for f in `find . -type d`; do
    o=$d/$f
    [ -d $o ] && echo ln -s $o $f/.d && ln -s $o $f/.d
done

find . -name .c -type l -delete
for d in $top/*.repack/override; do
    echo cd $d
    cd $d
    for f in `find . -type d`; do
        o=$c/$f
        [ -d $o ] && echo ln -s $o $f/.c && ln -s $o $f/.c
    done
done
