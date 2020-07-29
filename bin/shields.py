#!/usr/bin/env python3
import glob

from PIL import Image

shield_scale = 16

def scale(t):
    return tuple(shield_scale * s for s in t)


for src_file in glob.glob('entity/banner/*.png'):
    src_img = Image.open(src_file)
    pattern = src_img.crop((8, 8, 168, 328))
    new_img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    new_img.paste(pattern, (32, 32))
    new_img.save(src_file.replace('banner', 'shield'))
