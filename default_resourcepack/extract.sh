#!/bin/sh
set -x

places=(/Applications/MultiMC.app/Data/libraries/com/mojang/minecraft)
cd ~/clarity/default_resourcepack

for f in $places; do
    loc="$f/$1/minecraft-$1-client.jar"
    if [ -f "$loc" ]; then
	rm -rf [a-df-z]*
	unzip -qq "$loc" -x '*.class' log4j2.xml META-INF/'*'
	rm -f pack.*
	to_rm=`cat .gitignore`
	#rm -rf $to_rm
	find */ -type f -print0 | xargs -0 chmod -w
	git add .
    else
	echo missing
	ls -l $loc
    fi
done
