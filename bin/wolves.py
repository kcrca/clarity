#!/usr/bin/env python3

# This program generates the various wolf textures based on the default one for each wolf type. The "tame" variant
# is more open, friendly eyes, created from the default eyeball color, and the angry wolf is created by pasting an
# "angry eyes" image on top of the default one.

__author__ = 'arnold'

import glob

from PIL import Image

import clip

dst_dir = clip.directory('textures', 'entity', 'wolf')
angry = Image.open(f'{dst_dir}/wolf_angry_overlay.png')
angry_baby = Image.open(f'{dst_dir}/wolf_angry_overlay_baby.png')

# Every wolf we want to modify has a tame variant, so this captures them all
for img_file in glob.glob(f'{dst_dir}/wolf*_tame*.png'):
    # Open the generic of the wolf type
    img = Image.open(img_file.replace('_tame', '')).convert('RGBA')

    # Make the "tame" eyes
    if 'baby' in img_file:
        eye_px = (255, 255, 255, 255)
        img.putpixel((5, 19), eye_px)
        img.putpixel((6, 18), eye_px)
        img.putpixel((9, 18), eye_px)
        img.putpixel((10, 19), eye_px)
    else:
        eye_px = img.getpixel((4, 6))
        img.putpixel((5, 5), eye_px)
        img.putpixel((8, 5), eye_px)
    img.save(img_file)

    # Overlay the "angry" mask
    if 'baby' in img_file:
        img.paste(angry_baby, mask=angry_baby)
    else:
        img.paste(angry, mask=angry)
    img.save(img_file.replace('tame', 'angry'))
