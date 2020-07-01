#!/bin/sh

rm -rf *
unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*'
#rm -f pack.*
find */ -type f -print0 | xargs -0 chmod -w
git add .
