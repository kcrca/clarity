#!/usr/bin/env python

import os
import random
import shutil
import sys
import getopt
import ConfigParser
import re
import Image
import json

__author__ = 'arnold'

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

texture_dir = os.path.dirname(os.path.abspath(__file__))
painting_dir = os.path.join(texture_dir, 'painting')
paintings = os.path.join(painting_dir, 'paintings_kristoffer_zetterstrand.png')
texture = os.path.join(texture_dir, 'items', 'painting.png')
animation = os.path.join(texture_dir, 'items', 'painting.png.mcmeta')
breakout_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(texture_dir)))), 'site', 'paintings')

paintings_img = Image.open(paintings).convert('RGBA')
assert paintings_img.size[0] == paintings_img.size[1]
img_size = paintings_img.size[0]
img_scale = img_size / 256
pixel_scale = 16 * img_scale
max_size = 4 * pixel_scale
min_size = 1 * pixel_scale

images = []
for x in range(0, 7):
    images.append((x, 0, 1, 1))
for x in range(0, 5):
    images.append((x * 2, 2, 2, 1))
for x in range(0, 2):
    images.append((x, 4, 1, 2))
images.append((0, 6, 4, 2))
for x in range(0, 6):
    images.append((x * 2, 8, 2, 2))
for x in range(0, 3):
    images.append((x * 4, 12, 4, 4))
for y in range(0, 2):
    images.append((12, 4 + y * 3, 4, 3))
# Set the seed to prevent the png changing each time this is run. Otherwise we end up checking a new png file each time
# we run the script.
random.seed(13)
random.shuffle(images)

assert len(images) == 26

item_img = Image.new('RGBA', (max_size, max_size * len(images)), (0, 0, 0, 0))
thumb_scale = 4

frames = []
for i in range(0, len(images)):
    art_desc = images[i]
    x, y, w, h = [v * pixel_scale for v in art_desc]
    art_img = paintings_img.crop((x, y, x + w, y + h))
    art_thumb_img = art_img.copy().resize((w * thumb_scale, h * thumb_scale))
    art_thumb_img.save(os.path.join(breakout_dir, "painting_%02d.png" % i))
    # scale image up to fix in max size
    art_scale = min(max_size / w, max_size / h)
    if art_scale > 1:
        art_img = art_img.resize((w * art_scale, h * art_scale))
    art_size = art_img.size
    placement = [(max_size - v) / 2 for v in art_size]
    item_img.paste(art_img, (placement[0], placement[1] + i * max_size))
    # put in the frame multiple time so animation interpolation only happens part of the time
    for j in range(0, 5):
        frames.append(i)

item_img.save(texture)

anim_json = {
    "animation": {
        "frametime": 15,
        "interpolate": True,
        "frames": frames,
    }
}
with open(animation, 'w') as f:
    json.dump(anim_json, f, indent=2)
