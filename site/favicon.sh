#!/bin/sh
set -e

cd `dirname $0`

convert favicon.png -define icon:auto-resize=64,48,32,16 favicon.ico
