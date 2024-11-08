#!/usr/bin/env python3

# Generates derived files from the paintings. This includes:
#
#     (*) The animated item, which cycles through the individual paintings.
#     (*) Broken-out images of each individual painting for the site.
__author__ = 'arnold'

import glob
import json
import os
from pathlib import Path

from PIL import Image

import clip

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

texture_dir = clip.directory('textures')
paintings = os.path.join(texture_dir, 'painting')
texture = os.path.join(texture_dir, 'item', 'painting.png')
animation = os.path.join(texture_dir, 'item', 'painting.png.mcmeta')
breakout_dir = clip.directory('site', 'paintings')

unused = ('back', 'earth', 'fire', 'water', 'wind')
images = tuple(filter(lambda p: Path(p).stem not in (unused), glob.glob(os.path.join(paintings, '*.png'))))

thumb_scale = 4

frames = []
max_size = 0
art_imgs = []
for img_file in images:
    art_img = Image.open(img_file)
    w, h = art_img.size
    if os.path.exists(img_file + ".mcmeta"):
        # Assuming all animated images are square
        h = w
        art_img = art_img.crop((0, 0, w, w))
    if h == w:
        frames += 5 * (len(art_imgs),)
        art_imgs.append((img_file, (w, h), art_img))
        max_size = max(w, h, max_size)

art_imgs.sort(key=lambda desc: (desc[1], desc[0]))

item_img = Image.new('RGBA', (max_size, max_size * len(art_imgs)), (0, 0, 0, 0))
for i in range(0, len(art_imgs)):
    # scale image up to max size
    img_file, size, art_img = art_imgs[i]
    w, h = size
    art_scale = min(max_size / w, max_size / h)
    if art_scale > 1:
        art_img = art_img.resize((int(w * art_scale), int(h * art_scale)), 0)
    art_size = art_img.size
    placement = [int((max_size - v) / 2) for v in art_size]
    item_img.paste(art_img, (placement[0], placement[1] + i * max_size))
    # put in the frame multiple time so animation interpolation only happens part of the time

item_img.save(texture, optimize=True)

anim_json = {
    "animation": {
        "frametime": 15,
        "interpolate": True,
        "frames": frames,
    }
}
with open(animation, 'w') as f:
    json.dump(anim_json, f, indent=2)
