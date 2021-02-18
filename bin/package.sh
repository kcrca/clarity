#!/bin/sh

# This script builds up the various packs from the source.
#
# It makes many conservative assumptions so it can avoid rebuilding
# things if not needed.

set -e

bin=`dirname $0`
cd $bin/..
top="$PWD"
packs=$top/site/packs
version=`cat core/pack_version.txt`

dirs=(clarity connectivity continuity changes current beguile)
rm -rf $packs $dirs

# Create the packs dir
test -d $packs || mkdir -p $packs
out=$top/repack.out
echo Output in "$out"
rm -rf $out
cp /dev/null $out

which -a python3

echo Regenerating derived files
for f in bin/*.py; do
    script=`basename $f`
    case $script in
	report.py|gui_arrows.py)
	    ;;
	colorize.py)
	    for cfg in `find $top -name colorize.cfg`; do
		d=`dirname $cfg`
		echo ... python3 $script $d 2>&1 | tee -a $out3
		python3 $f $d
	    done
	    ;;
	*)
	    echo ... python3 $script $a 2>&1 | tee -a $out
	    python3 $f >> $out
	    ;;
    esac
done
echo ... python3 gui_arrows.py $a 2>&1 | tee -a $out
python3 bin/gui_arrows.py >> $out

to_title() {
    echo "$(tr a-z A-Z <<< ${1:0:1})${1:1}"
}

license() {
    name=$1
    ucname=$2
    (echo "<p>${ucname}: Part of the Clarity Resource Pack Family for Minecraft.<br>" && cat License.html) > $name/License.html
    (echo "${ucname}: Part of the Clarity Resource Pack Family for Minecraft." && cat License.txt) > $name/License.txt
}

# This function will build a single zip file
do_zip() {
    (
	name=$1
	ucname=`to_title $name`
	zipname="${ucname}_$version.zip"
	cd $name

	echo Building $zipname
	if false; then
	    # If enabled, this would use optipng to optimize the size of the
	    # png files. This saves about 10% in the zip file sizes. Doesn't
	    # seem worth it, especially since it would require some serious
	    # testing to make sure that no bug in optipng changed the reults.
	    echo ... optipng
	    find . -name '*.png' -print0 | xargs -0 optipng -q -preserve
	    echo ... zip
	fi
	# The "-o" flag says to make the mod time on the zip file the same
	# as the most recent mod time on any of the files. This lets the
	# zip file's mod time stand for the most recent change in the entire
	# zipped directory.
	zip -rDqoy "$packs/$zipname" *
    )
}

# Creates special subparts of the resource pack set as a standalone pack
do_create() {
    name=$1
    shift
    mkdir -p $name
    tar c -C clarity "$@" | tar xf - -C $name
    # Trivial implementation of repack for this case
    tar c -C $name.repack/override . | tar xf - -C $name
    find $name \( -name '*.pxm' -o -name '*.psd' -o -name '*.py*' \) -print0 | xargs -0 rm
}

echo ... Repacking
python3 repack/repack.py >> $out || ( cat $out ; exit 1)

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
    "changes")
	mkdir -p $name
	tar c -C $name.repack/override . | tar xf - -C $name
	find $name/assets/minecraft/textures/block -type d -depth 1 -print0 | xargs -0 rm -r
	find $name \( -name '*.pxm' -o -name '*.psd' -o -name '*.py' -o -name '*.sh' \) -print0 | xargs -0 rm
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
    "current")
        # This pack is nearly entirely built by current.py, but this is not.
	cp $name.repack/override/pack*.png $name/
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

echo Building "ClarityFamily_$version.zip"
(
    cd $packs
    zip -q "ClarityFamily_$version.zip" *.zip
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
echo ... site/favicon.sh $version
site/favicon.sh $version
