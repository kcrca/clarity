#!/bin/sh

set -x
dir=$(dirname $0)
typeset -a file
typeset -a parents
file=(`awk '/^#/{next} {print $1}' $dir/reparent.txt`)
parents=(`awk '/^#/{next} {print $2}' $dir/reparent.txt`)

i=0
echo ${#parents}
while [ "${file[$i]}" != "" ]; do
    echo ${file[$i]} ${parents[$i]}
    ((i++))
done
