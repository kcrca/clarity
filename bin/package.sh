#!/bin/zsh

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
path=($top/venv/bin $path)

setopt nullglob

# Suss out the top-level version numbers, which is 1.X
v=$version
top_version=$version
until [[ $v:r == $v ]]; do
    top_version=$v
    v=$v:r
done

# Removed 'changes' because miencraft time seems to longer run long enough to see it
dirs=(contraption clarity connectivity continuity current call_out call_out_all beguile)

# Create the packs dir
test -d $packs || mkdir -p $packs
out=$top/repack.out
echo Output in "$out"
rm -rf $out
cp /dev/null $out

newest_zip=($(ls -t $packs))
newer=($(find bin core/assets -newer $packs -type f ! -name '.*' | head))
if (( $#newest_zip > 0 && $#newer > 0 )); then
    echo Regenerating derived files
    for f in bin/*.py; do
	script=`basename $f`
	case $script in
	    report.py)
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
else
    echo No new derived files
fi

to_title() {
    echo "$(tr a-z A-Z <<< ${1:0:1})${1:1}"
}

license() {
    name=$1
    ucname=$2
    (echo "<p>${ucname}: Part of the Clarity Resource Pack Family for Minecraft.<br>" && cat License.html) >! $name/License.html
    (echo "${ucname}: Part of the Clarity Resource Pack Family for Minecraft." && cat License.txt) >! $name/License.txt
}

pack_format="$(grep pack_format core/pack.mcmeta)"
# This function will build a single zip file
do_zip() {
    (
	name=$1
	ucname=`to_title $name`
	zipname="${ucname}.$version.zip"
	echo Building $zipname
	cd $name
	# Strip the EXIF and other text tags from images
	# xargs isn't working directly here, so we use it to bunch up args only
	find . -name '*.png' -type f | xargs | while read l; do; eval exiv2 rm "$l"; done
	for f in $(find . -name '*.png.split'); do
	    rm $f $f:r
	done
	ed -s pack.mcmeta <<EOF
/pack_format/c
$pack_format
.
w
EOF
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
    find $name \( -name '*.ai' -o -name '*.px?' -o -name '*.psd' -o -name '*.py*' -o -name '*README*' \) -print0 | xargs -0 rm
    for f in $(find $name -name '*.png.split'); do
	rm $f $f:r
    done
}
 
echo ... Repacking
python3 repack/repack.py >> $out || ( cat $out ; echo Exit: 1: read $out ; exit 1)

test -h home || (rm -rf home && ln -s $HOME/Library/Application\ Support/minecraft home)
rm -f $packs/*${top_version}*.zip
# Works for a mac, should check for other configurations
for name in "${dirs[@]}"; do
    ucname=`to_title $name`
    zipname="${ucname}_$version"
    case "$name" in
    "beguile")
	do_create $name assets/minecraft/textures/gui
	;;
    "changes")
	mkdir -p $name
	tar c -C $name.repack/override . | tar xf - -C $name
	find $name/assets/minecraft/textures/block -type d -depth 1 -print0 | xargs -0 rm -r
	find $name \( -name '*.pxd' -o -name '*.psd' -o -name '*.py' -o -name '*.sh' \) -print0 | xargs -0 rm
	for f in $(find $name -name '*.png.split'); do
	    rm $f $f:r
	done
	;;
    "contraption")
	#cp -r $name.repack/override/* $name/
	mkdir -p $name
	rsync --safe-links -a $name.repack/override/* $name/
	;;
    "current")
        # This pack is nearly entirely built by current.py, but this is not.
	mkdir -p $name
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
    zip -q "ClarityFamily_$version.zip" *${version}.zip
)

echo Building site
for name in "${dirs[@]}"; do
    cp $name/pack_thumb.png site/${name}_thumb.png
done
(
    cd site
    ./build.sh
)
echo ... site/update_version.sh $version
site/update_version.sh $version
echo ... site/favicon.sh $version
site/favicon.sh $version
