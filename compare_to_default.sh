#!/bin/sh
diff -r default_resourcepack clarity | egrep -v '^Binary|textures/items: |: \.|clarity: pack'
