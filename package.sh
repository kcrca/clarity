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
cp /dev/null $out

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

function to_title() {
    echo "$(tr a-z A-Z <<< ${1:0:1})${1:1}"
}

# This function will build a single zip file
function do_zip() {
    (
	name=$1
	ucname=`to_title $name`
	cd $name
	rm -f $packs/$ucname.zip

	echo Building $ucname.zip
	# The "-o" flag says to make the mod time on the zip file the same
	# as the most recent mod time on any of the files. This lets the
	# zip file's mod time stand for the most recent change in the entire
	# zipped directory.
	zip -rDqoy $packs/$ucname.zip *
    )
}

# Creates special subparts of the texture pack set
function do_create() {
    name=$1
    ucname=`to_title $name`
    shift
    mkdir -p $ucname
    tar c -C clarity "$@" | tar xf - -C $ucname
    # Trivial implementation of repack for this case
    tar c -C $name.repack/override . | tar xf - -C $ucname
    find $name -name '*.pxm' -print0 | xargs -0 rm
}

echo ... Repacking
python repack/repack.py $f >> $out || ( cat $out ; exit 1)

rm -f home
# Works for a mac, should check for other configurations
ln -s $HOME/Library/Application\ Support/minecraft home
for name in "${dirs[@]}"; do
    ucname=`to_title $name`
    case "$name" in
      "beguile")
	do_create $name assets/minecraft/textures/gui
	;;
      *)
	;;
    esac
    do_zip $name
    (
	cd home/resourcepacks
	rm -f $ucname $ucname.zip $name $name.zip
	ln -s $packs/../$ucname .
    )
done
