#!/bin/sh

# This script copies models from the default texture pack and changes (or adds) their parents. It is useful for
# models where this change is the only one needed, since it means that future updates to the default pack are
# "inherited" during the build rather than frozen at the time of the decision for the reparenting.
#
# It reads 'reparent.txt' and, ignoring lines that start with '#', uses the first column for the glob that specifies
# the file name(s) and the second for the new parent.

dir=$(dirname $0)
cd $dir
orig=${PWD/core/default_resourcepack}

typeset -a patterns
typeset -a parents
patterns=( `awk '/^#/{next} {print $1}' reparent.txt` )
parents=( `awk '/^#/{next} {print $2}' reparent.txt` )

i=0
while [ "${patterns[$i]}" != "" ]; do
    parent=${parents[$i]}

    # expand the glob into a list of files
    typeset -a files
    files=$(cd $orig; echo ${patterns[$i]}.json)
    echo $files
    rm -f $files

    for f in $files; do
        (if grep -s '"parent"' $orig/$f > /dev/null; then
            sed -e '\+"parent"+s+: *".*"+: "'$parent'"+'
        else
            sed -e '1a\
\    "parent": "'$parent'",'
        fi) < $orig/$f > $f
    done
    ((i ++))
done
