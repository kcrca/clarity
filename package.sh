#!/bin/sh

# This script builds up the various packs from the source.
#
# It makes many conservative assumptions so it can avoid rebuilding
# things if not needed.

set -e

cd `dirname $0`

dirs=(clarity continuity connectivity beguile)
rm -rf packs $dirs

# Create the packs dir
test -d packs || mkdir packs
packs=$PWD/packs
out=$packs/repack.out
rm -f $out
touch $out

echo Regenerating derived files in core
for f in `find . -name '*.py'`; do
    dir=`dirname $f`
    script=`basename $f`
    case $script in
	report.py|repack.py)
	    ;;
	*)
	    (
		echo ... python $f 2>&1 | tee -a $out
		cd $dir
		python $script >> $out
	    )
	    ;;
    esac
done

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

# Creates special subparts of the texture pack set
function do_create() {
    name=$1
    shift
    echo ... Creating $name
    mkdir -p $name
    tar c -C clarity "$@" | tar xf - -C $name
    # Trivial implementation of repack for this case
    tar c -C $name.repack/override . | tar xf - -C $name
    find $name -name '*.pxm' | xargs rm
}

echo ... Repacking
python repack/repack.py $f >> $out || ( cat $out ; exit 1)

rm -f home
ln -s $HOME/Library/Application\ Support/minecraft home
for f in "${dirs[@]}"; do
    case "$f" in
      "beguile")
	do_create $f assets/minecraft/textures/gui assets/minecraft/textures/font
	;;
      *)
	;;
    esac
    do_zip $f
    (
	cd home/resourcepacks
	rm -f $f $f.zip
	ln -s $packs/../$f .
    )
done
