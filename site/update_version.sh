#!/bin/sh
set -e
cd `dirname $0`
ver_cur="$1"
[ x"$ver_cur" != x"" ] || (echo Must specify version ; exit 1)
ver_old=$(sed -E -n -e 's/^<.-- version: ([^ ]*) -->/\1/p' < index.html)

if [ "$ver_cur" != "$ver_old" ]; then
    echo ... Changing "'$ver_old'" to "'$ver_cur'"
    ver_old_re=$(echo "$ver_old" | sed -e 's/[.]/\\./g')
    ex index.html <<EOF
g/\\<$ver_old_re\\>/s//$ver_cur/g
w
q
EOF
fi

ts_cur=$(ls -l index.html | awk '{print $7,$6,$8}')
ts_old=$(sed -E -n -e 's/^ *<p class=.timestamp.>(.*)/\1/p' < index.html)
if [ "$ts_cur" != "$ts_old" ]; then
    echo ... Changing "'$ts_old'" to "'$ts_cur'"
    ex index.html <<EOF
/\\(<p class="timestamp">\\).*/s//\1$ts_cur/
w
q
EOF
fi
