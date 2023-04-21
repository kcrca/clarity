#!/usr/bin/env python3

import glob
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops

import clip

textures = Path(os.path.join(clip.directory('textures', 'entity', 'decorated_pot')))
items = Path(os.path.join(clip.directory('textures', 'item')))
parts = textures / 'parts'

pot_bg = Image.open(textures / 'decorated_pot_side.png')
sherd_bg = Image.open(parts / 'sherd.png')

for part in parts.glob('*.png'):
    if part.stem == 'sherd':
        continue
    which = part.stem
    img = Image.open(part)
    pot_img = pot_bg.copy()
    pot_img.paste(img, mask=img)
    pot_img.save(textures / f'{which}_pottery_pattern.png')
    masked_img = sherd_bg.copy()
    masked_img.paste(img, (-2, 0), mask=img)
    sherd = Image.new('RGBA', img.size)
    sherd.paste(masked_img, mask=sherd_bg)
    sherd.save(items / f'{which}_pottery_sherd.png')
