#!/bin/sh

set -e

cd `dirname $0`

for html in ${html} call_out.html; do
    ver_cur="$1"
    [ x"$ver_cur" != x"" ] || (echo Must specify version ; exit 1)
    ver_old=$(sed -E -n -e 's/^<.-- version: ([^ ]*) -->/\1/p' < ${html})
    ver_old_re=$(echo "$ver_old" | sed -e 's/[.]/\\./g')

    ts_cur=$(stat -f '%Sm' ${html})

    rm -f ${html}.new
    ex ${html} <<EOF
g/\\<$ver_old_re\\>/s//$ver_cur/g
/CopyrightBegin/+,/CopyrightEnd/-d
/CopyrightBegin/r ../License.html
/\\(<p class="timestamp">\\).*/s//\1Page Last Edited: $ts_cur/
w ${html}.new
q
EOF

    # If it's been changed, update the edit date
    if diff -I'"timestamp"' ${html}{,.new} >/dev/null; then
	rm ${html}.new
    else
	mv ${html}.new ${html}
    fi
done
