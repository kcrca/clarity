#!/usr/bin/env python3

# Generates derived files from the paintings. This includes:
#
#     (*) The animated item, which cycles through the individual paintings.
#     (*) Broken-out images of each individual painting for the site.
import glob

__author__ = 'arnold'

import os
import random
import json
from PIL import Image
import clip

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

texture_dir = clip.directory('textures')
paintings = os.path.join(texture_dir, 'painting')
texture = os.path.join(texture_dir, 'item', 'painting.png')
animation = os.path.join(texture_dir, 'item', 'painting.png.mcmeta')
breakout_dir = clip.directory('site', 'paintings')

images = list(glob.glob(os.path.join(paintings, '*.png')))
images.remove(os.path.join(paintings, 'back.png'))

# Set the seed to prevent the png changing each time this is run. Otherwise we end up checking a new png file each time
# we run the script.
random.seed(13)
random.shuffle(images)

thumb_scale = 4

frames = []
max_size = 0
for img_file in images:
    art_img = Image.open(img_file)
    w, h = art_img.size
    max_size = max(w, h, max_size)

item_img = Image.new('RGBA', (max_size, max_size * len(images)), (0, 0, 0, 0))
for i in range(0, len(images)):
    art_img = Image.open(images[i])
    w, h = art_img.size
    # scale image up to fix in max size
    art_scale = min(max_size / w, max_size / h)
    if art_scale > 1:
        art_img = art_img.resize((int(w * art_scale), int(h * art_scale)))
    art_size = art_img.size
    placement = [int((max_size - v) / 2) for v in art_size]
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
