#!/bin/sh

dir=$(dirname $0)
cd $dir
orig=${PWD/core/default_resourcepack}

typeset -a patterns
typeset -a parents
patterns=(`awk '/^#/{next} {print $1}' reparent.txt`)
parents=(`awk '/^#/{next} {print $2}' reparent.txt`)

i=0
while [ "${patterns[$i]}" != "" ]; do
    typeset -a files
    files=$(cd $orig ; echo ${patterns[$i]}.json)
    parent=${parents[$i]}
    echo $files
    rm -f $files
    for f in $files; do
	(if grep -s '"parent"' $orig/$f >/dev/null; then
	    sed -e '\+"parent"+s+: *".*"+: "'$parent'"+'
	else
	    sed -e '1a\
\    "parent": "'$parent'",'
	fi) < $orig/$f > $f
    done
    ((i++))
done
