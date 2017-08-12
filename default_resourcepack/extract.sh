#!/bin/sh

unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*' mcmod.info
find . -type f | xargs chmod -w
