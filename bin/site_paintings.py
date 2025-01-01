#!/usr/bin/env python3
# Generates the versions of the paintings files that are published on the website.

from pathlib import Path

from PIL import Image

import clip
from pynecraft.values import paintings

src = Path(clip.directory('textures', 'painting'))
dst = Path(clip.directory('site', 'painting'))

canvases = set(paintings.values())
for p in canvases:
    try:
        src_img = Image.open((src / p.name).with_suffix('.png'))
    except FileNotFoundError:
        print(f'Missing: {p.size[0]}x{p.size[1]} {p.name}')
        continue
    dims = p.size
    new_size = (64 * dims[0], 64 * dims[1])
    dst_img = src_img.resize(new_size, Image.Resampling.NEAREST)
    dst_img.save((dst / p.name).with_suffix('.png'))
