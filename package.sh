#!/bin/sh

# This script builds up the various packs from the source.
#
# It makes many conservative assumptions so it can avoid rebuilding
# things if not needed.
#
# The file core.zip is built for date testing purposes only.
#

# If any dirs are specified on the command line, build only those
cd `dirname $0`

do_clean=0
if [ x"$1" = x"--clean" ]; then
    do_clean=1
    shift
fi

declare -a dirs
dirs=("$@")
if [ -z "$dirs" ]; then
    dirs=(clarity connectivity continuity beguile)
fi

if [ $do_clean -gt 0 ]; then
    rm -rf packs $dirs
fi

# Create the packs dir
test -d packs || mkdir packs
packs=$PWD/packs

# If this script is newer than core.zip, start from scratch
if [ packs/core.zip -ot $0 ]; then
    echo Build script is new, starting from scratch
    rm packs/core.zip
fi

# If any file in core is newer than core.zip, generate things. This could
# be more specific by checking only relevant files.
if [ ! -f packs/core.zip -o ! -z "`find core -newer packs/core.zip`" ]; then
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
	zip -rDqoy $packs/$1.zip *
    )
}

# Build core.zip
do_zip core

rm -f home
ln -s $HOME/Library/Application\ Support/minecraft home
for f in "${dirs[@]}"; do
    zip=packs/$f.zip
    if [ ! -f $zip -o $zip -ot packs/core.zip -o $zip -ot repack/repack.py -o $zip -ot $f.repack/repack.cfg ] \
	|| ( [ -f $zip ] &&  find $f.repack -newer $zip | grep -q . ); then
	if [ "$f" = "beguile" ]; then
	    # This isn't technically a "repack", but we use the "repack" directory for overrides
	    # because inventing a new kind of suffix seems weird
	    echo Creating $f
	    mkdir -p $f
	    tar c -C clarity assets/minecraft/textures/gui assets/minecraft/textures/font | tar xf - -C $f
	    tar c -C $f.repack/override . | tar xf - -C $f
	    rm $f/*.pxm
	else
	    echo Repacking $f
	    out=packs/$f.repack.out
	    rm -f $out
	    if python repack/repack.py core $f > $out; then
		:
	    else
		cat $out 
		exit 1
	    fi
	fi
	do_zip $f
	(
	    cd home/resourcepacks
	    rm -f $f $f.zip
	    #ln -s $packs/$f.zip .
	    ln -s $packs/../$f .
	)
    fi
done
