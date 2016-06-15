#!/bin/sh

unzip -qq "$@" -x '*.class' log4j2.xml META-INF/'*' -d /tmp/t
