#!/bin/sh
diff -r default_resourcepack clarity | egrep -v '^Binary|texture.item: |: \.|clarity: pack'
