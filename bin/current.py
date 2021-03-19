#!/usr/bin/env python3

# This program generates a small texture pack that adds redstone power numbers where
# they can be added.

import configparser
import json
import os
import shutil
import sys

from PIL import Image
from clip import *

scale = 0.75


top = directory('top')
os.chdir(top)

config_file = directory('config', 'current.cfg')
config = configparser.ConfigParser()
config.read(config_file)

current_states = 'current/assets/minecraft/blockstates'
current_models = 'current/assets/minecraft/models/block'
current_textures = 'current/assets/minecraft/textures/block'
if (os.path.exists('current')):
    shutil.rmtree('current')
os.makedirs(current_states)
os.makedirs(current_models)
os.makedirs(current_textures)

pack = json.load(open('core/pack.mcmeta'))
pack['pack']['description'] = "Clarity texture showing power levels."
dump('current/pack.mcmeta', pack)

c_blockstates = directory('blockstates')
d_blockstates = directory('defaults', 'blockstates')

current_digits = Image.open('%s/block/current.png' % directory('textures')).convert('RGBA')
w = current_digits.size[0]
h = current_digits.size[1] / 16
for i in range(0, 16):
    digit_img = current_digits.crop((0, i * h, w, (i + 1) * h))
    full_digit = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    full_digit.paste(digit_img, (0, 0))
    pixels = full_digit.load()
    for x in range(0, 16):
        for y in range(0, 16):
            if pixels[x, y] == (213, 53, 53, 255):
                pixels[x, y] = (93, 0, 0, 255)
    full_digit.paste(digit_img, (0, 16))
    full_digit.save('%s/current_%02d.png' % (current_textures, i), optimize=True)
    dump('%s/current_%02d.png.mcmeta' % (current_textures, i), {'animation': {'interpolate': True, 'frametime': 60}})

current_cfg = config.items('default')
for model, args in current_cfg:
    values = args.split()
    y = float(values[0])
    h_off = h
    if y > 16:
        y -= (16)
        h_off = 16
    scaled_w = scale * w
    scaled_h = scale * h_off
    blocks = values[1:]
    parent_model = '%s/current_%s.json' % (current_models, model)
    face = {
        'uv': [0, 0, w, h_off],
        'texture': '#current'
    }
    dump(parent_model, {'ambientocclusion': False,
                        'elements': [
                            {
                                'from': [8 - scaled_w / 2, y, 8],
                                'to': [8 + scaled_w / 2, y + scaled_h, 8],
                                'shade': False,
                                'faces': {
                                    'north': face,
                                    'south': face
                                }
                            },
                            {
                                'from': [8, y, 8 - scaled_w / 2],
                                'to': [8, y + scaled_h, 8 + scaled_w / 2],
                                'shade': False,
                                'faces': {
                                    'east': face,
                                    'west': face
                                }
                            }
                        ]
                        })
    for i in range(1, 16):
        dump('%s/current_%s_%02d.json' % (current_models, model, i),
             {'parent': 'block/current_%s' % model, 'textures':
                 {'current': 'block/current_%02d' % i}
              })
    for block in blocks:
        state = None
        for d in c_blockstates, d_blockstates:
            json_path = '%s/%s.json' % (d, block)
            if os.path.exists(json_path):
                state = json.load(open(json_path))
                break
        if not state:
            print('Cannot find blockstate for %s' % block)
            sys.exit(1)

        try:
            multipart = state['multipart']
        except KeyError:
            variants = state['variants']
            del state['variants']
            multipart = []
            state['multipart'] = multipart
            for k, v in variants.items():
                clause = k.split(',')
                clauses = []
                for c in clause:
                    name, value = c.split('=')
                    clauses.append({name: value})
                multipart.append({'when': {'AND': clauses}, 'apply': v})
        for i in range(1, 16):
            multipart.append({'when': {'power': i}, 'apply': {'model': 'block/current_%s_%02d' % (model, i)}})
        dump('%s/%s.json' % (current_states, block), state)
