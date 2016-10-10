#!/bin/sh

set -e

cd `dirname $0`

ver_cur="$1"
[ x"$ver_cur" != x"" ] || (echo Must specify version ; exit 1)
ver_old=$(sed -E -n -e 's/^<.-- version: ([^ ]*) -->/\1/p' < index.html)
ver_old_re=$(echo "$ver_old" | sed -e 's/[.]/\\./g')

ts_cur=$(ls -l index.html | awk '{print $7,$6,$8}')

rm -f index.html.new
ex index.html <<EOF
g/\\<$ver_old_re\\>/s//$ver_cur/g
/CopyrightBegin/+,/CopyrightEnd/-d
/CopyrightBegin/r ../License.html
w index.html.new
q
EOF

# If it's been changed, update the edit date
if cmp -s index.html index.html.new; then
    rm index.html.new
else
    mv index.html.new index.html
    ex index.html <<EOF
/\\(<p class="timestamp">\\).*/s//\1Page Last Edited: $ts_cur/
EOF
fi
