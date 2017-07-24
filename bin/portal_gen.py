#!/usr/bin/env python

# This program generates the portal image.

__author__ = 'arnold'

from PIL import Image
import clip


def line_at(xy, c):
    for p in range(0, 16):
        img.putpixel((xy[0], xy[1] + p), c)


band_colors = (
    (203, 75, 255, 200),
    (172, 60, 244, 200),
    (158, 55, 233, 200),
    (133, 39, 217, 200))
width = 16
frames = 16 + len(band_colors) - 2
img = Image.new('RGBA', (width, frames * width), color=(55, 0, 157, 160))
img_y = 0
for i in range(0, 16):
    img_y = i * width

    for b in range(0, min(i + 1, len(band_colors))):
        left = (7 - i + b) % 16
        right = (8 + i - b) % 16
        color = band_colors[b]
        line_at((left, img_y), color)
        line_at((right, img_y), color)
img_y += 16
line_at((7, img_y), band_colors[0])
line_at((8, img_y), band_colors[0])
line_at((6, img_y), band_colors[2])
line_at((9, img_y), band_colors[2])
line_at((5, img_y), band_colors[3])
line_at((10, img_y), band_colors[3])
img_y += 16
line_at((7, img_y), band_colors[0])
line_at((8, img_y), band_colors[0])
line_at((6, img_y), band_colors[3])
line_at((9, img_y), band_colors[3])
img.save(clip.directory('textures', 'blocks/portal.png'))
