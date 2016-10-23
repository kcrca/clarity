#!/bin/sh

# This script builds up the various packs from the source.
#
# It makes many conservative assumptions so it can avoid rebuilding
# things if not needed.

set -e

cd `dirname $0`
top=$PWD
packs=$top/site/packs
version=`cat core/pack_version.txt`

dirs=(clarity continuity connectivity changes charged beguile)
rm -rf $packs $dirs

# Create the packs dir
test -d $packs || mkdir -p $packs
out=$top/repack.out
rm -rf $out
cp /dev/null $out

echo Regenerating derived files
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

function license() {
    name=$1
    ucname=$2
    (echo "<p>${ucname}: Part of the Clarity Resource Pack Family for Minecraft.<br>" && cat License.html) > $name/License.html
    (echo "${ucname}: Part of the Clarity Resource Pack Family for Minecraft." && cat License.txt) > $name/License.txt
}

# This function will build a single zip file
function do_zip() {
    (
	name=$1
	ucname=`to_title $name`
	zipname="$ucname $version.zip"
	cd $name

	echo Building $zipname
	# The "-o" flag says to make the mod time on the zip file the same
	# as the most recent mod time on any of the files. This lets the
	# zip file's mod time stand for the most recent change in the entire
	# zipped directory.
	zip -rDqoy "$packs/$zipname" *
    )
}

# Creates special subparts of the resource pack set as a standalone pack
function do_create() {
    name=$1
    shift
    mkdir -p $name
    tar c -C clarity "$@" | tar xf - -C $name
    # Trivial implementation of repack for this case
    tar c -C $name.repack/override . | tar xf - -C $name
    find $name -name '*.pxm' -print0 | xargs -0 rm
}

echo ... Repacking
python repack/repack.py $f >> $out || ( cat $out ; exit 1)

rm -f home
# Works for a mac, should check for other configurations
ln -s $HOME/Library/Application\ Support/minecraft home
for name in "${dirs[@]}"; do
    ucname=`to_title $name`
    zipname="$ucname $version"
    case "$name" in
    "beguile")
	do_create $name assets/minecraft/textures/gui
	;;
    "changes"|"charged")
	mkdir -p $name
	tar c -C $name.repack/override . | tar xf - -C $name
	find $name/assets/minecraft/textures/blocks -type d -depth 1 -print0 | xargs -0 rm -r
	find $name \( -name '*.pxm' -o -name '*.py' -o -name '*.sh' \) -print0 | xargs -0 rm
	;;
    "connectivity")
	# Strip out everything but the continuity info and pack stuff
	# First remove files we don't need.
	for f in $(find connectivity \( -name mcpatcher -o -name 'pack*' \) -prune -o -print); do
	    test -f $f && rm $f
	done
	# Now delete all the empty dirs we left behind
	find -d connectivity -type d -empty -exec rmdir '{}' \;
	;;
    *)
	;;
    esac
    license $name $ucname
    do_zip $name
    (
	cd home/resourcepacks
	rm -f ${ucname}* ${name}*
	ln -s $top/$name "$(basename "$zipname" .zip)"
    )
done

echo Building "ClarityFamily $version.zip"
(
    cd $packs
    zip -q "ClarityFamily $version.zip" *.zip
)

echo Building site
for name in "${dirs[@]}"; do
    cp $name/pack_thumb.png site/${name}_thumb.png
done
for f in `find site -name build.sh`; do
    (
	echo ... $f
	dir=`dirname $f`
	cd $dir
	build.sh
    )
done
echo ... site/update_version.sh $version
site/update_version.sh $version
echo ... site/split_paintings.sh
site/split_paintings.sh $top/clarity/assets/minecraft/textures/painting/paintings_kristoffer_zetterstrand.png
