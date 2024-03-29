#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.

__author__ = 'arnold'

import json
import os

from PIL import Image

import clip

NUM_FRAMES = 16

# If this ever changes it could be worth the trouble to generalize, but for now I'm
# just assuming the structure of the images.

texture_dir = clip.directory('textures')
block_dir = os.path.join(texture_dir, 'block')
item_dir = os.path.join(texture_dir, 'item')
model_dir = os.path.join(clip.directory('models'), 'block')


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
    anims[side].save(os.path.join(item_dir, '%s_%s.png' % (detector, side)), optimize=True)
