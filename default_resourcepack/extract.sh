#!/bin/sh

unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*' mcmod.info
find . -type f -print0 | xargs -0 chmod -w
