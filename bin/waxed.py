#!/usr/bin/env python3
import configparser
import glob
import os
import re
from pathlib import Path

from PIL import Image

import clip

config_file = clip.directory('config', 'waxed.cfg')
config = configparser.ConfigParser()
config.read(config_file)

basic = config['basic']
textures = Path(clip.directory('textures', 'block'))
default_overlay = Image.open(textures / basic.get('default_overlay')).convert('RGBA')
ignore_re = re.compile(basic.get('ignore'))
blocks_dir = Path(clip.directory('textures', 'block'))
overlays_spec = basic.get('overlays')
overlays = {}
for k in overlays_spec.split():
    overlays[k] = Image.open(blocks_dir / f'waxed_{k}_overlay.png')

# Clean out existing blockstates and models for waxed stuff. Assumes there are NO custom files here.
for file in (
        glob.glob(clip.directory('blockstates') + "/waxed_*")+
        glob.glob(clip.directory('models', 'block') + "/waxed_*")
):
    os.remove(file)

for in_file in glob.glob(clip.directory('defaults', 'blockstates') + "/waxed_*"):
    if ignore_re.match(in_file):
        continue
    out_file = in_file.replace('default_resourcepack', 'core')
    with open(in_file) as in_fp:
        in_str = in_fp.read()
        out_str = in_str.replace("block/", "block/waxed_")
        # We have no waxed versio of the "_on" state
        out_str = out_str.replace('waxed_lightning_rod_on', 'lightning_rod_on')
        with open(out_file, 'w') as out_fp:
            out_fp.write(out_str)

blocks = set()
for in_file in (
        glob.glob(clip.directory('defaults', 'models', 'block') + "/*copper*") +
        glob.glob(clip.directory('defaults', 'models', 'block') + "/*lightning_rod*")):
    if ignore_re.search(in_file):
        continue
    out_file = in_file.replace('default_resourcepack', 'core')
    out_dir = os.path.dirname(out_file)
    out_base = os.path.basename(out_file)
    out_file = f'{out_dir}/waxed_{out_base}'
    with open(in_file) as in_fp:
        in_str = in_fp.read()
        out_str = re.sub(r'(block/)([^/]*copper[^/][^"]*)', r"\1waxed_\2", in_str)
        out_str = re.sub(r'(block/)([^/]*lightning_rod(?!_on)[^/][^"]*)', r"\1waxed_\2", out_str)
        for block in re.finditer(r'\bwaxed_\w*', out_str):
            blocks.add(block.group())
        with open(out_file, 'w') as out_fp:
            out_fp.write(out_str)

for block in blocks:
    overlay = default_overlay
    for k, v in overlays.items():
        if k in block:
            overlay = v
            break

    try:
        img = Image.open(blocks_dir / f'{block.replace("waxed_", "")}.png')
    except FileNotFoundError as e:
            continue
    orig_mode = img.mode
    img = img.convert('RGBA')
    clip.alpha_composite(img, overlay, (0, 0))
    img = img.convert(orig_mode)
    img.save(blocks_dir / f'{block}.png')
