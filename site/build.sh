#!/bin/sh
set -e
cd $(dirname $0)
for f in src/*/; do
  name=$(dirname $f/.)
  out=$(basename $name).gif
  if test ! -f $out || find $name build.sh -type f -newer $out | grep -s . >&/dev/null; then
    case $out in
    download.gif)
      echo - convert -delay 200 $name/\*.png -loop 0 -resize 32x32 $out
      convert -delay 200 $name/*.png -loop 0 -scale 32x32 $out
      ;;
    *)
      if [ -f $name/build.sh ]; then (
        echo ~ $name/build.sh
        cd "$name"
        ./build.sh
      ); else
        echo - convert -delay 200 $name/\*.png -loop 0 -resize 750x483 $out
        convert -delay 200 $name/*.png -loop 0 -resize 750x483 $out
      fi
      ;;
    esac
  fi
done
