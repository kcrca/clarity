#!/bin/zsh
set -e

cd ~/clarity

src=$PWD
dst=/Applications/MultiMC.app/Data/instances/$1/.minecraft
[[ -d $dst ]] || exec file $dst

rm -f home
ln -s $dst home
cd home
rm -f allowed_symlinks.txt
echo '[regex].*' > allowed_symlinks.txt
rm -f resourcepacks/core
ln -s $src/core resourcepacks/
ln -s $src/call_out* resourcepacks/
[[ -f options.txt.bak ]] | cp options.txt options.txt.bak
ex - options.txt << \EOF
/^advancedItemTooltips:/s/:.*/:true
/^autoJump:/s/:.*/:false
/^bobView:/s/:.*/:false
/^biomeBlendRadius:s/:.*/0
/^chatScale:/s/:.*/:0.75
/^darkMojangStudiosBackground:/s/:.*/:true
/^key_key.pickItem:/s/:.*/:key.keyboard.p
/^key_key.socialInteractions:/s/:.*/:key.keyboard.unknown
/^key_key.use:/s/:.*/:key.keyboard.left.alt
/^operatorItemsTab:/s/:.*/:true
/^soundCategory_master:/s/:.*/:0.0
/^reducedDebugInfo:/s:.*/false
wq
EOF
