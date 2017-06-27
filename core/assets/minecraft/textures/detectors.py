#!/usr/bin/env python

import os
from PIL import Image
import json

NUM_FRAMES = 16

__author__ = 'arnold'

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

texture_dir = os.path.dirname(os.path.abspath(__file__))
blocks_dir = os.path.join(texture_dir, 'blocks')
items_dir = os.path.join(texture_dir, 'items')
model_dir = os.path.join(texture_dir, "..", "models", "block")


def open_img(model, which):
    img_path = os.path.join(texture_dir, model["textures"][which] + ".png")
    return Image.open(img_path).convert("RGBA")


detector = 'daylight_detector'
anims = {}
for i in range(0, NUM_FRAMES):
    model_path = os.path.join(model_dir, '%s_%02d.json' % (detector, i))
    with open(model_path) as f:
        model = json.load(f)
    imgs = {}
    for side in ("top", "ns", "ew"):
        img = imgs[side] = open_img(model, side)
        try:
            anim = anims[side]
        except KeyError:
            anim = anims[side] = Image.new("RGBA", (img.size[0], img.size[1] * NUM_FRAMES))
        anim.paste(img, (0, i * img.size[1]))
for side in anims:
    anims[side].save(os.path.join(items_dir, '%s_%s.png' % (detector, side)))
