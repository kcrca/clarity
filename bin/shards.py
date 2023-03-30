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
shard_bg = Image.open(parts / 'shard.png')

for part in parts.glob('*.png'):
    if part.stem == 'shard':
        continue
    which = part.stem
    img = Image.open(part)
    pot_img = pot_bg.copy()
    pot_img.paste(img, mask=img)
    pot_img.save(textures / f'{which}_pottery_pattern.png')
    masked_img = shard_bg.copy()
    masked_img.paste(img, (-2, 0), mask=img)
    shard = Image.new('RGBA', img.size)
    shard.paste(masked_img, mask=shard_bg)
    shard.save(items / f'{which}_pottery_shard.png')
