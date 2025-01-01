#!/usr/bin/env python3

# This program generates powder snow outline. It reads in the upper-left quadrant, doubles its height (weird,
# but that's how it's done), and flips it to the other quadrants.

__author__ = 'arnold'

import sys

from PIL import Image
from PIL.Image import Transpose

import clip

img_path = clip.directory('textures', 'misc/powder_snow_outline.png')
ul_img_path = clip.directory('textures', 'misc/powder_snow_outline_ul.png')

if len(sys.argv) > 1 and sys.argv[1] == '-r':
    img = Image.open(img_path)
    half_width = int(img.size[0] / 2)
    half_height = int(img.size[1] / 2)
    quarter_height = int(img.size[1] / 4)
    ul_img = Image.new('RGBA', (half_width, quarter_height))
    for y in range(0, half_height, 2):
        row = img.crop((0, y, half_width, y + 1))
        ul_img.paste(row, (0, int(y / 2)))
    ul_img.save(ul_img_path)
else:
    ul_img = Image.open(ul_img_path)

    # double the height (again, huh?)
    ul_w, ul_h = ul_img.size
    img = Image.new('RGBA', (ul_w * 2, ul_h * 4))
    for y in range(0, ul_h):
        row = ul_img.crop((0, y, ul_w, y + 1))
        img.paste(row, (0, y * 2))
        img.paste(row, (0, y * 2 + 1))

    img.paste(img.crop((0, 0, ul_w, ul_h * 2)).transpose(Transpose.FLIP_LEFT_RIGHT), (ul_w, 0))
    img.paste(img.crop((0, 0, ul_w * 2, ul_h * 2)).transpose(Transpose.FLIP_TOP_BOTTOM), (0, ul_h * 2))
    img.save(img_path)
