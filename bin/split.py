#!/usr/bin/env python3

import os
from pathlib import Path

from PIL import Image

import clip

textures = Path(os.path.join(clip.directory('textures')))
for split in textures.glob('**/*.png.split'):
    f = open(split)
    pattern = f.readline().strip()
    which = ' '.join(f.readlines()).split()
    img_file = split.parent / split.stem
    img = Image.open(img_file)
    assert img.size[1] % len(which) == 0
    h = int(img.size[1] / len(which))
    for i, n in enumerate(which):
        out = split.parent / ((pattern % n) + '.png')
        img.crop((0, i * h, img.size[0], (i + 1) * h)).save(out)
