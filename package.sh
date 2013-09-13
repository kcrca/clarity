#!/bin/sh -x
(cd core/assets/minecraft/textures ; python colorize.py)
(cd core/assets/minecraft/textures/gui/container ; python panels.py)
rm -rf packs
mkdir packs
packs=$PWD/packs
for f in clarity clearity connectivity continuity; do
    python repack/repack.py core $f
    (cd $f ; zip ../packs/$f.zip -r *)
    (
	cd home/resourcepacks
	rm -f $f $f.zip
	ln -s $packs/$f.zip .
    )
done
