#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.

__author__ = 'arnold'

import os
import json
from PIL import Image
import clip

NUM_FRAMES = 16

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

font_dir = os.path.join(clip.directory('defaults', 'textures'), 'font')
font_file = os.path.join(font_dir, 'ascii.png')
texture_dir = os.path.join(clip.directory('textures'), 'block')

font_img = Image.open(font_file).convert('RGBA')

digit_imgs = {}
for i in range(0, 10):
    img = digit_imgs[i] = font_img.crop((i * 8, 24, i * 8 + 8, 32))
    digit_pixels = digit_imgs[i].load()
    for x in range(0, 8):
        for y in range(0, 8):
            if digit_pixels[x, y][0] > 0:
                digit_pixels[x, y] = (0xea, 00, 00)
