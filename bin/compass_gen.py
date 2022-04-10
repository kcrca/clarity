#!/usr/bin/env python3

# Generate the model files for the compass. There is an individual prop file for each displayed angle variation, and a
# primary model file that lists all those and when to show them. The variation in each file is how much to rotate the
# image.

__author__ = 'arnold'

import json
import os
import shutil

import clip

TICKS = 32
TICK_DIGIT_COUNT = clip.num_digits(TICKS)

TICK_FRACTION = 1.0 / TICKS
HALF_TICK_FRACTION = TICK_FRACTION / 2

FP_SCALE = [0.3, 0.3, 0.3]
FP_TRANSLATION = [-1, 4, 1]
FP_X_ROT = -65
FP_Y_ROT = 0  # Generate each override file for each angle "tick"

dir = clip.directory('models')
os.chdir(dir)

overrides = []
for i in range(0, TICKS + 1):
    day_frac = i * TICK_FRACTION

    model = 'item/compass/compass_%0*d' % (TICK_DIGIT_COUNT, i % TICKS)
    json_path = model + '.json'
    angle_frac = day_frac
    if i > 0:
        angle_frac -= HALF_TICK_FRACTION
    overrides.append({"predicate": {"angle": angle_frac}, "model": model})

    with open(json_path, 'w') as f:
        angle = ((angle_frac + HALF_TICK_FRACTION) * 360 + 270) % 360
        json.dump({
            "parent": "item/base_compass",
            "display": {
                "firstperson_righthand": {
                    "rotation": [FP_X_ROT, FP_Y_ROT, -angle + 27],
                    "translation": FP_TRANSLATION,
                    "scale": FP_SCALE
                },
                "firstperson_lefthand": {
                    "rotation": [FP_X_ROT, FP_Y_ROT, angle - 22],
                    "translation": FP_TRANSLATION,
                    "scale": FP_SCALE
                }
            }
        }, f, indent=4, sort_keys=True)

# Now generate the primary model file that lists all the overrides generated above.
with open('item/compass.json', 'w') as f:
    json.dump({
        "parent": "item/base_compass",
        "overrides": overrides
    }, f, indent=4, sort_keys=True)


def toRecovery(src, dst=None):
    old_text = open(src, 'r').read()
    new_text = old_text.replace('compass', 'recovery_compass')
    open(src.replace('compass', 'recovery_compass'), 'w').write(new_text)


# Recovery compass is just modified compass
toRecovery("item/compass.json")
toRecovery("item/base_compass.json")
shutil.rmtree("item/recovery_compass", ignore_errors=True)
shutil.copytree("item/compass", "item/recovery_compass", copy_function=toRecovery)
