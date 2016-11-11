#!/usr/bin/env python

import json
import shutil
import os
import math

ticks = 32
tick_digit_cnt = int(math.ceil(math.log(ticks, 10)))

tick_fraction = 1.0 / ticks
half_tick_fraction = tick_fraction / 2


def clear_out_tree(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
    return dir_name


model_dir = clear_out_tree('models/item/compass')

overrides = []

scale = [0.3, 0.3, 0.3]
translation = [-1, 4, 1]
xrot = -65
yrot = 0

for i in range(0, ticks + 1):
    day_frac = i * tick_fraction

    name = 'compass_%0*d' % (tick_digit_cnt, i % ticks)
    model = 'item/compass/%s' % name
    json_path = model + '.json'
    angle_frac = day_frac
    if i > 0:
        angle_frac -= half_tick_fraction
    overrides.append({"predicate": {"angle": angle_frac}, "model": model})

    with open('models/%s' % json_path, 'w') as f:
        angle = ((angle_frac + half_tick_fraction) * 360 + 270) % 360
        json.dump({
            "parent": "item/generated",
            "textures": {
                "layer0": "items/compass"
            },
            "display": {
                "firstperson_righthand": {
                    "rotation": [xrot, yrot, -angle + 27],
                    "translation": translation,
                    "scale": scale
                },
                "firstperson_lefthand": {
                    "rotation": [xrot, yrot, angle - 22],
                    "translation": translation,
                    "scale": scale
                }
            }
        }, f, indent=4, sort_keys=True)

with open('models/item/compass.json', 'w') as f:
    json.dump({
        "parent": "item/generated",
        "textures": {
            "layer0": "items/compass",
        },
        "overrides": overrides
    }, f, indent=4, sort_keys=True)
