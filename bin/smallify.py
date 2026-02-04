#!/usr/bin/env python3

import sys

from PIL import Image

from clip import has_transparency

if len(sys.argv) <= 1:
    sys.exit(0)

in_img = Image.open(sys.argv[1])
if has_transparency(in_img):
    out_img = in_img
else:
    out_img = in_img.convert('P', palette=Image.Palette.ADAPTIVE)
out_img.save(sys.argv[2])
