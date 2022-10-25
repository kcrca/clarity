#!/usr/bin/env python3
import configparser
import copy
import json
import os
import re
import shutil
import sys
from pathlib import Path

import clip

blockstates = {}
blocks = {}
items = {}

collections = {'block': blocks, 'item': items}

blockstates_dir = 'contraption/assets/minecraft/blockstates'
models_dir = 'contraption/assets/minecraft/models/block'


def populate(which, orig, *where):
    d = Path(clip.directory(*where, is_defaults=orig))
    for f in d.glob('**/*.json'):
        name = str(f)[len(str(d)) + 1:-5]
        model = json.load(open(f))
        model['orig'] = orig
        model['name'] = name
        which[name] = model
    return which


def kidize(which):
    for name, model in which.items():
        if 'parent' in model:
            parent = parent_model(model)
            if parent:
                parent.setdefault('kids', []).append(name)


def parent_model(model):
    parent = model['parent']
    collection, file = split_model_name(parent)
    if collection == 'builtin':
        return None
    c = collections[collection]
    return c[file]


def split_model_name(parent):
    dir, file = parent.split('/', 1)
    collection = normalize(dir)
    return collection, file


def normalize(name):
    return re.sub('minecraft:', '', name)


def convert(coords):
    for i in range(len(coords)):
        nv = round(coords[i] / 2 + 4, 5)
        if coords[i] % 2 == 0:
            nv = int(nv)
        coords[i] = nv


def model_refs(d):
    if isinstance(d, dict) and 'model' in d:
        yield d
    for v in d if isinstance(d, list) else d.values():
        if isinstance(v, (dict, list)):
            yield from model_refs(v)


def write_from(which, dir):
    for m in sorted(which):
        d = which[m]
        if 'write' in d and d['write']:
            del d['write']
            del d['name']
            del d['orig']
            if 'kids' in d:
                del d['kids']
            out = f'{dir}/{m}.json'
            Path(out).parent.mkdir(exist_ok=True)
            clip.dump(out, d)


def main():
    top = clip.directory('top')
    os.chdir(top)

    config_file = clip.directory('config', 'contraption.cfg')
    config = configparser.ConfigParser()
    config.read(config_file)

    if os.path.exists('contraption'):
        shutil.rmtree('contraption')
    os.makedirs(blockstates_dir)
    os.makedirs(models_dir)

    pack = json.load(open('core/pack.mcmeta'))
    pack['pack']['description'] = "Clarity pack to make redstone mechanisms clearer."
    clip.dump('contraption/pack.mcmeta', pack)

    # Read in all the models
    for orig in (True, False):
        populate(blockstates, orig, 'blockstates')
        populate(blocks, orig, 'models', 'block')
        populate(items, orig, 'models', 'item')

    # Add 'kids' values to all models
    kidize(blocks)
    kidize(items)

    config_items = config.items('default')
    n, shrink_list = config_items[0]
    assert(n == 'shrink')
    shrink = shrink_list.split()

    for block_name in shrink:
        blockstate = blockstates[block_name]
        refs = list(model_refs(blockstate))
        for ref in refs:
            model_name = ref['model']
            _, model_name = split_model_name(model_name)
            new_model_name = f'{model_name}_cntr'
            ref['model'] = f'minecraft:block/{new_model_name}'
            blockstate['write'] = True
            if new_model_name not in blocks:
                model = blocks[block_name]
                elem_model = model
                while 'elements' not in elem_model:
                    elem_model = parent_model(elem_model)

                new_model = copy.deepcopy(model)
                new_model['name'] = new_model_name
                new_model['write'] = True
                new_elems = copy.deepcopy(elem_model['elements'])
                new_model['elements'] = new_elems
                blocks[new_model_name] = new_model
                for elem in new_elems:
                    convert(elem['from'])
                    convert(elem['to'])
                    try:
                        convert(elem['rotation']['origin'])
                    except KeyError:
                        # This may not exist
                        pass
                    for face in elem['faces'].values():
                        if 'uv' not in face:
                            # Otherwise the default is the new smaller area
                            face['uv'] = [0, 0, 16, 16]
                        if 'cullface' in face:
                            del face['cullface']

    write_from(blockstates, blockstates_dir)
    write_from(blocks, models_dir)


if __name__ == '__main__':
    sys.exit(main())
