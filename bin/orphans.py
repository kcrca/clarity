import os

__author__ = 'arnold'

import glob
import json
import clip
import re


def find_models(data):
    if data is None:
        return []
    if isinstance(data, list):
        models = []
        for member in data:
            models += find_models(member)
        return models
    if isinstance(data, dict):
        try:
            return (data['model'],)
        except KeyError:
            pass
        models = []
        for key in data:
            models += find_models(data[key])
        return models
    return []


def find_textures(data):
    textures = []
    try:
        textures_block = data['textures']
        for texture_name in textures_block:
            textures.append(path_part(textures_block[texture_name]))
    except KeyError:
        pass
    return textures


def models_for(state):
    return find_models(state)


def models_under(variants):
    models = []
    for variant_key in variants:
        v = variants[variant_key]
        print(type(v))
        if isinstance(v, list):
            for variant in v:
                try:
                    models += (variant['model'],)
                except KeyError:
                    pass
        else:
            try:
                models += (v['model'],)
            except KeyError:
                pass
        try:
            models += (variants['model'],)
        except KeyError:
            pass
    return models


def path_part(model_name):
    return model_name.replace('minecraft:', '')


def import_model(model_name):
    model_name = path_part(model_name)
    if model_name in models:
        return
    if model_name.startswith('builtin/'):
        return
    try:
        with open(os.path.join(clip.directory('models'), model_name + '.json')) as fp:
            model = json.load(fp)
    except IOError:
        with open(os.path.join(clip.directory('defaults', 'models'), model_name + '.json')) as fp:
            model = json.load(fp)
    models[model_name] = model
    try:
        del unused_models[model_name]
    except KeyError:
        pass

    try:
        import_model(model['parent'])
    except KeyError:
        pass


subpath_re = re.compile(r'([^/]+/[^/]+)\.[a-z]+$')

blockstates = {}
models = {}
unused_models = {}

# First we pull in all the models for the blocks, using the blockstates files as the roots of the tree.

for file in glob.glob('%s/*.json' % clip.directory('defaults', 'blockstates')):
    with open(file) as fp:
        blockstates[os.path.basename(file)] = json.load(fp)

for file in glob.glob('%s/*.json' % clip.directory('blockstates')):
    with open(file) as fp:
        blockstates[os.path.basename(file)] = json.load(fp)

default_models = clip.directory('defaults', 'models')

# Find all of our own models, and store them as possibly unused
for file in glob.glob('%s/block/*.json' % clip.directory('models')):
    model_name = subpath_re.search(file).group(1)
    unused_models[model_name] = True

for block_name in blockstates:
    block = blockstates[block_name]
    for model_name in models_for(block):
        model_name = path_part(model_name)
        try:
            del unused_models[model_name]
        except KeyError:
            pass
        import_model(model_name)

# Next we look at all the items

for file in glob.glob('%s/item/*.json' % clip.directory('models')) + \
            glob.glob('%s/item/*.json' % clip.directory('defaults', 'models')):
    model_name = subpath_re.search(file).group(1)
    import_model(model_name)

print('Models: %s' % len(models))
if len(unused_models) > 0:
    print('UNUSED models:\n   ', end=' ')
    print('\n    '.join(sorted(unused_models)))

# Now lets look for unused textures
textures = {}
unused_textures = {}
# Textures that are not reachable by the regular techniques
special_textures = (
    'block/books',
    'block/current',
    'block/destroy_stage_0',
    'block/destroy_stage_1',
    'block/destroy_stage_2',
    'block/destroy_stage_3',
    'block/destroy_stage_4',
    'block/destroy_stage_5',
    'block/destroy_stage_6',
    'block/destroy_stage_7',
    'block/destroy_stage_8',
    'block/destroy_stage_9',
    'block/portal', # animation for the nether portal
    'block/lava_flow',
    'block/note_block_notes',
    'block/water_flow',
    'item/clock_font',

    # Used in generating UI places where things are to be put
    'item/empty_armor_slot_boots',
    'item/empty_armor_slot_chestplate',
    'item/empty_armor_slot_helmet',
    'item/empty_armor_slot_leggings',
    'item/empty_armor_slot_shield',
    'item/blank_banner_pattern',
    'item/carpet_for_llama',
    'item/netherite_ingot',

    #
)

for file in glob.glob('%s/item/*.png' % clip.directory('textures')) + glob.glob(
        '%s/block/*.png' % clip.directory('textures')):
    texture_name = subpath_re.search(file).group(1)
    if texture_name not in special_textures:
        unused_textures[texture_name] = True

for model_name in models:
    model = models[model_name]
    for texture_name in find_textures(model):
        # print '%s: %s' % (model_name, texture_name)
        textures[texture_name] = True
        try:
            del unused_textures[texture_name]
        except KeyError:
            pass

print('Textures: %d' % len(textures))
if len(unused_textures) > 0:
    print('UNUSED textures:\n   ', end=' ')
    print('\n    '.join(sorted(unused_textures)))
    os.sys.exit(1)
