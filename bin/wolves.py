#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.

__author__ = 'arnold'

import glob

from PIL import Image

import clip

dst_dir = clip.directory('textures', 'entity', 'wolf')
overlay = Image.open(f'{dst_dir}/wolf_angry_overlay.png')

for img_file in glob.glob(f'{dst_dir}/wolf*_tame.png'):
    img = Image.open(img_file.replace('_tame', '')).convert('RGBA')
    eye_px = img.getpixel((4, 6))
    img.putpixel((5, 5), eye_px)
    img.putpixel((8, 5), eye_px)
    img.save(img_file)
    img.paste(overlay, mask=overlay)
    img.save(img_file.replace('tame', 'angry'))
