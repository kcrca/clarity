#!/bin/sh
set -e
cd `dirname $0`
cur="$1"
[ x"$cur" != x"" ] || (echo Must specify version ; exit 1)
old=$(sed -E -n -e 's/^<.-- version: ([^ ]*) -->/\1/p' < index.html)
if [ "$cur" == "$old" ]; then
    exit 0
fi

echo ... Changing "'$old'" to "'$cur'"
old_re=$(echo "$old" | sed -e 's/[.]/\\./g')
ex index.html <<EOF
g/\\<$old_re\\>/s//$cur/g
w
q
EOF
