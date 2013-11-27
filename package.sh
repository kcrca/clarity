#!/bin/sh

# This script builds up the various packs from the source.
#
# It makes many conservative assumptions so it can avoid rebuilding
# things if not needed.
#
# The file core.zip is built for date testing purposes only.
#

# If any dirs are specified on the command line, build only those
declare -a dirs
dirs=("$@")
if test -z "$dirs"; then
    dirs=(clarity clearity connectivity continuity)
fi

# Create the packs dir
test -d packs || mkdir packs
packs=$PWD/packs

# If this script is newer than core.zip, start from scratch
if test packs/core.zip -ot $0; then
    echo Build script is new, starting from scratch
    rm packs/core.zip
fi

# If any file in core is newer than core.zip, generate things. This could
# be more specific by checking only relevant files.
if test ! -f packs/core.zip -o ! -z "`find core -type f -newer packs/core.zip`"; then
    echo Regenerating derived files in core
    (cd core/assets/minecraft/textures ; python colorize.py)
    (cd core/assets/minecraft/textures/gui/container ; python panels.py)
fi

# This function will build a single zip file
function do_zip() {
    (
	cd $1 
	rm -f $packs/$1.zip

	echo Building $1.zip
	# The "-o" flag says to make the mod time on the zip file the same
	# as the most recent mod time on any of the files. This lets the
	# zip file's mod time stand for the most recent change in the entire
	# zipped directory.
	zip -rDqo $packs/$1.zip *
    )
}

# Build core.zip
do_zip core

for f in "${dirs[@]}"; do
    if test ! -f packs/$f.zip -o packs/$f.zip -ot packs/core.zip -o packs/$f.zip -ot repack/repack.py; then
	echo Repacking $f
	python repack/repack.py core $f > packs/$f.repack.out
	do_zip $f
	(
	    cd home/resourcepacks
	    rm -f $f $f.zip
	    ln -s $packs/$f.zip .
	)
    fi
done