#!/bin/zsh

# Generate a report of the files in the resource pack.
#
# Files that are listed as "Missing" or "Same" are ones that maybe should be
# included. Other missing or unchanged files are filtered out.
#
# The list of "Changed" files is for reference, but there are going to be lots
# of them. This is why they are sorted to the end of the report.
#
# If a file is not where it is expected to be, it is marked as "UNEXPECTED" and
# listed first in the report.

# First go to the top of the resource pack texture area
top=`dirname $0`
cd $top

# Files that are expected to be only in the resource pack (internal use)
added=(
    .gitignore
    report.sh
    font/alternate.properties
    font/default.properties
    textures/gui/container/parts
    'report_.*\.config'
    '.*_colored\.png'
    '.*\.pxm'
    '.*\.py'
    '.*\.cfg'
    '.*/.'
)

config=$1
if [ -z "$config" ]; then
    config=report_default.config
fi
. $config

if [ ! -d $other ]; then
    echo Cannot find $other 1>&2
    exit 1
fi

# Create the sed file that will massage the diff output into useful info
sed_file=/tmp/clarity_report.sed
rm -f $sed_file
cat > $sed_file << EOF

# Varios tmp files
/\.swp$/d
/\/.$/d
/\~$/d

# DS_Store are added on Mac OSX
/\.DS_Store/d

# Changed files (will be lots of these)
/^Binary files/{
    s//Changed:/
    s/ and .*//
}

# Files that are the same
/^Files /{
    s//Same: /
    s/ and .*//
}

# In the default pack but not in this one
/^Only in ${other:gs,/,\\/,}/ {
    s//Missing@ /
    s/: /\//
    s/@/:/
    s,: /,: ,
}

# Added in this resource pack
/^Only in \./{
    s//Extra@ /
    s,: ,/,
    s/@ \//: /
}

# Change (for example) "Same: ./foo" to "Same: foo"
s/: \.\//: /
EOF

# Files that are expected to be only in the resource pack (internal use)
for f in $added; do
    e=${f:gs,/,\\/,}
    cat >> $sed_file << EOF
/^Extra: $e\$/d
/.*: $e\$/s//UNEXPECTED: & $e/
EOF
done

# Files that are expected to be identical (should be very few)
for f in $same; do
    e=${f:gs,/,\\/,}
    cat >> $sed_file << EOF
/^Same: $e\$/d
/.*: $e\$/s//UNEXPECTED: & $e/
EOF
done

# Files that are expected to be missing (which means we use the default)
for f in $missing; do
    e=${f:gs,/,\\/,}
    cat >> $sed_file << EOF
/^Missing: $e\$/d
/.*: $e\$/s//UNEXPECTED: & $e/
EOF
done

# Files that are expected to be changed but were matched by general rules that
# complained about them
for f in $suppress_complaint; do
    e=${f:gs,/,\\/,}
    cat >> $sed_file << EOF
/^UNEXPECTED: Changed: $e/ {
    s/.*/Changed: $e/
}
EOF
done

# Force a sort order for the reporting
cat >> $sed_file << \EOF
/^UNEXPECTED/s//A&/
/^Changed:/s//Z&/
EOF

diff -rs . $other | sed -f $sed_file | sort | sed -e 's/^AUNEXPECTED/UNEXPECTED/' -e 's/^ZChanged/Changed/'
