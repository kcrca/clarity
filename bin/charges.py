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

config_file = directory('config', 'charges.cfg')
config = configparser.ConfigParser()
config.read(config_file)

charge_states = 'charges/assets/minecraft/blockstates'
charge_models = 'charges/assets/minecraft/models/block'
charge_textures = 'charges/assets/minecraft/textures/block'
if (os.path.exists('charges')):
    shutil.rmtree('charges')
os.makedirs(charge_states)
os.makedirs(charge_models)
os.makedirs(charge_textures)

pack = json.load(open('core/pack.mcmeta'))
pack['pack']['description'] = "Clarity's chargess showing"
dump('charges/pack.mcmeta', pack)

c_blockstates = directory('blockstates')
d_blockstates = directory('defaults', 'blockstates')

charges_digits = Image.open('%s/block/charges.png' % directory('textures')).convert('RGBA')
w = charges_digits.size[0]
h = charges_digits.size[1] / 16
for i in range(0, 16):
    digit_img = charges_digits.crop((0, i * h, w, (i + 1) * h))
    full_digit = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    full_digit.paste(digit_img, (0, 0))
    pixels = full_digit.load()
    for x in range(0, 16):
        for y in range(0, 16):
            if pixels[x, y] == (213, 53, 53, 255):
                pixels[x, y] = (93, 0, 0, 255)
    full_digit.paste(digit_img, (0, 16))
    full_digit.save('%s/charges_%02d.png' % (charge_textures, i))
    dump('%s/charges_%02d.png.mcmeta' % (charge_textures, i), {'animation': {'interpolate': True, 'frametime': 60}})

charges_cfg = config.items('default')
for model, args in charges_cfg:
    values = args.split()
    y = float(values[0])
    h_off = h
    if y > 16:
        y -= (16)
        h_off = 16
    scaled_w = scale * w
    scaled_h = scale * h_off
    blocks = values[1:]
    parent_model = '%s/charges_%s.json' % (charge_models, model)
    face = {
        'uv': [0, 0, w, h_off],
        'texture': '#charges'
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
        dump('%s/charges_%s_%02d.json' % (charge_models, model, i),
             {'parent': 'block/charges_%s' % model, 'textures':
                 {'charges': 'block/charges_%02d' % i}
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
            multipart.append({'when': {'power': i}, 'apply': {'model': 'block/charges_%s_%02d' % (model, i)}})
        dump('%s/%s.json' % (charge_states, block), state)
