#!/bin/sh

unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*'
find . -type f | xargs chmod -w
