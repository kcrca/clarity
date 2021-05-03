#!/bin/sh

rm -rf [a-df-z]*
unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*'
#rm -f pack.*
find */ -type f -print0 | xargs -0 chmod -w
rm -rf `cat .gitignore`
git add .
