#!/usr/bin/env python3
import configparser
import glob
import os
import re
from pathlib import Path

from PIL import Image

import clip

# We want textures for the waxed copper stuff so you can tell. It should be only slightly different from the unwaxed,
# but see-able. Since there are multiple exposures of things to be waxed, we never do custom waxed textures, we always
# do an overlay on the unwaxed.
#
# There are only waxable copper blocks, no item-only things. So the list of waxed things to texture is the same as the
# list of waxed-type blocks. So we do this all in a few steps.
#
# 1. We remove all waxed_* models. All are generated, and we don't want any crap left behind if names change, etc.
#
# 2. We look through vanilla's blockstates to find all waxed_* type blocks. For each block:
#      a. For each blockstate, we make waxed_* from the existing one, or ours if there is one, replacing block/*copper
#      with block/waxed_*copper. We remember the list of models we encounter.
#      b. Then we do the analogous thing for the items/ directory.
#
# 3. For each block or item model encountered in step 2, we make a waxed_ copy of either ours or theirs, modified to
# use waxed textures. From these we also build a list of the copper blocks we need.
#
# 4. For each copper block generated from step 3, we look to see if there is a waxed_copper_* overlay. If not we
# use the default overlay ('waxed_overlay.png'). We create waxed_*.png with an alpha-composite.
#
# This does _NOT_ handle entities, like copper armor or chests. Haven't figured that out yet.
#
# For all waxable blocks, this gives us:
#   (*) Superseding blockstates and items that refer to the waxed_ block and item models.
#   (*) waxed_* block and item models that are like the unwaxed ones but using the waxed versions of the textures.
#   (*) Waxed version of the textures.
#   (*) For overridden items, simple item models that use the overridden block textures.
#
# Lightning rods are copper, but don't say "copper", so in all the above, "copper" means "(copper|lightning_rod)". But
# we avoid lightning_rod_on because that's just white, it doesn't vary by exposure or waxing.
#
# Also, not every copper thing can be waxed, so the config lists types of copper files to ignore.

config_file = clip.directory('config', 'waxed.cfg')
config = configparser.ConfigParser()
config.read(config_file)

basic = config['basic']
textures_dir = Path(clip.directory('textures'))
default_overlay = Image.open(textures_dir / 'block' / basic.get('default_overlay')).convert('RGBA')
ignore_re = re.compile(basic.get('ignore'))
blocks_dir = Path(clip.directory('textures', 'block'))
simple_items_re = re.compile('|'.join(basic.get('simple_items').split()))

# Clean out existing blockstates and models for waxed stuff..
for file in (glob.glob(clip.directory('blockstates') + "/waxed_*") +
             glob.glob(clip.directory('items') + "/waxed_*") +
             glob.glob(clip.directory('models') + "/*/waxed_*")):
    os.remove(file)


def in_and_out(in_path: str) -> tuple[str, str]:
    our_path = in_path.replace('default_resourcepack', 'core')
    if Path(our_path).exists():
        in_path = our_path
    out_path = our_path
    if 'waxed' not in out_path:
        out_path = re.sub(r'(.*)/(.*)', r'\1/waxed_\2', our_path)
    return in_path, out_path


def translate(model, out_file):
    with (open(model) as in_fp):
        in_str = in_fp.read()
        out_str = re.sub(r'(block|item)/(\w*(copper|lightning_rod(?!_on))\w*)\b', r'\1/waxed_\2', in_str)
        with open(out_file, 'w') as fp:
            fp.write(out_str)
        return out_str


def remember(store, out_str):
    for texture in re.finditer(r'(block|item)/waxed_\w+', out_str):
        key = texture.group().replace('waxed_', '')
        # dumb special case
        if key == 'block/copper':
            key = 'block/copper_block'
        store.add(key)


# Look through the blockstates, creating new ones and new items/ entries also
simple_items = set()
models = set(basic.get('add_models').split())
for block_state in glob.glob(clip.directory('defaults', 'blockstates') + "/waxed_*"):
    base_name = re.search(r'(\w+)\.json', block_state).group(1)
    if ignore_re.match(block_state):
        continue
    in_file, out_file = in_and_out(block_state)
    out_str = translate(in_file, out_file)
    remember(models, out_str)

    # Now we create the items/ for the waxed item in the same way
    item_state = block_state.replace('blockstates', 'items')
    in_item, out_item = in_and_out(item_state)
    out_str = translate(in_item, out_item)
    remember(models, out_str)
v1 = True
# Generate the waxed versions of the models
textures = set()
for model in models:
    if ignore_re.match(model):
        continue
    in_file, out_file = in_and_out(clip.directory('defaults', 'models') + f'/{model}.json')
    if v1:
        out_str = translate(in_file, out_file)
        remember(textures, out_str)
    else:
        with open(in_file) as in_fp:
            in_str = in_fp.read()
            out_str = re.sub(r'(block|itemº)/([^/]*(copper|lightning_rod)[^/][^"]*)', r"\1/waxed_\2", in_str)
            for texture in re.finditer(r'((block|item)/waxed_\w+)', out_str):
                textures.add(texture.group(1))
            with open(out_file, 'w') as out_fp:
                out_fp.write(out_str)

with open(f'/tmp/{int(v1)}', 'w') as fp:
    print('\n'.join(sorted(textures)), file=fp)

for texture in textures:
    if v1:
        texture = texture.replace('/', '/waxed_')
    overlay = default_overlay
    override = blocks_dir.parent / f'{re.sub(r"(exposed|weathered|oxidized)_", "", texture)}_overlay.png'
    out_file = textures_dir / f'{texture}.png'
    in_file = str(out_file).replace('/waxed_', '/')
    if override.exists():
        overlay = Image.open(override)
    try:
        img = Image.open(in_file)
    except FileNotFoundError as e:
        print(f'Warning: skipping {texture}.png')
        continue
    orig_mode = img.mode
    img = img.convert('RGBA')
    clip.alpha_composite(img, overlay, (0, 0))
    img = img.convert(orig_mode)
    img.save(out_file)
