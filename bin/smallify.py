#!/usr/bin/env python3

import sys

from PIL import Image

if len(sys.argv) <= 1:
    sys.exit(0)

in_img = Image.open(sys.argv[1])
out_img = in_img.convert('P', palette=Image.Palette.ADAPTIVE)
out_img.save(sys.argv[2])
