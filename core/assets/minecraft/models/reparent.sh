#!/bin/sh

dir=$(dirname $0)
cd $dir
orig=${PWD/core/default_resourcepack}

typeset -a files
typeset -a parents
files=(`awk '/^#/{next} {print $1}' reparent.txt`)
parents=(`awk '/^#/{next} {print $2}' reparent.txt`)

i=0
while [ "${files[$i]}" != "" ]; do
    file=${files[$i]}.json
    parent=${parents[$i]}
    echo $file
    rm -f $file
    (if grep -s '"parent"' $orig/$file >/dev/null; then
	sed -e '\+"parent"+s+: *".*"+: "'$parent'"+'
    else
	sed -e '1a\
\    "parent": "'$parent'",'
    fi) < $orig/$file > $file
    ((i++))
done
