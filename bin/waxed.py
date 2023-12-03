#!/usr/bin/env python3
import glob
import os
import re

from PIL import Image

import clip

for in_file in glob.glob(clip.directory('defaults', 'blockstates') + "/waxed_*"):
    if '_ore' in in_file or 'raw_' in in_file:
        continue
    out_file = in_file.replace('default_resourcepack', 'core')
    with open(in_file) as in_fp:
        in_str = in_fp.read()
        out_str = in_str.replace("block/", "block/waxed_")
        with open(out_file, 'w') as out_fp:
            out_fp.write(out_str)

blocks = set()
for in_file in glob.glob(clip.directory('defaults', 'models', 'block') + "/*copper*"):
    if '_ore' in in_file or 'raw_' in in_file:
        continue
    out_file = in_file.replace('default_resourcepack', 'core')
    out_dir = os.path.dirname(out_file)
    out_base = os.path.basename(out_file)
    out_file = "%s/waxed_%s" % (out_dir, out_base)
    with open(in_file) as in_fp:
        in_str = in_fp.read()
        out_str = re.sub(r'(block/)([^/]*copper[^/][^"]*)', r"\1waxed_\2", in_str, 100)
        for block in re.finditer(r'\bwaxed_\w*', out_str):
            blocks.add(block.group())
        with open(out_file, 'w') as out_fp:
            out_fp.write(out_str)

blocks_dir = clip.directory('textures', 'block')
overlay = Image.open(blocks_dir + '/waxed_overlay.png')
overlay_td = Image.open(blocks_dir + '/waxed_trapdoor_overlay.png')
for block in blocks:
    img = Image.open(blocks_dir + '/%s.png' % block.replace('waxed_', ''))
    orig_mode = img.mode
    img = img.convert('RGBA')
    clip.alpha_composite(img, overlay_td if 'trapdoor' in block else overlay, (0, 0))
    img = img.convert(orig_mode)
    img.save(blocks_dir + '/%s.png' % block)
