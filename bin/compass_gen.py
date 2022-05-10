#!/usr/bin/env python3

# Generate the model files for the compass. There is an individual prop file for each displayed angle variation, and a
# primary model file that lists all those and when to show them. The variation in each file is how much to rotate the
# image.

__author__ = 'arnold'

import json
import math
import os
import shutil

import numpy as np
from PIL import ImageColor, Image
from PIL import ImageDraw

import clip

TICKS = 32
TICK_DIGIT_COUNT = clip.num_digits(TICKS)
TICK_FRACTION = 1.0 / TICKS
HALF_TICK_FRACTION = TICK_FRACTION / 2

FP_SCALE = [0.5, ] * 3
FP_TRANSLATION = [-1, 2, 1]
FP_X_ROT = -65
FP_Y_ROT = 0

IMG_SIZE = 512
IMG_MID = IMG_SIZE / 2.0
NEEDLE_WIDTH = IMG_SIZE * 0.05

TIP = 0.9 * IMG_SIZE
N_POINT = (IMG_MID, TIP)
S_POINT = (IMG_MID, IMG_SIZE - TIP)
L_MID_POINT = (IMG_MID - NEEDLE_WIDTH, IMG_MID)
R_MID_POINT = (IMG_MID + NEEDLE_WIDTH, IMG_MID)
REC_L_MID_POINT = (NEEDLE_WIDTH, IMG_MID)
REC_R_MID_POINT = (IMG_SIZE - NEEDLE_WIDTH, IMG_MID)
REC_S_POINT = (IMG_MID, IMG_MID - NEEDLE_WIDTH)
coords = [N_POINT, L_MID_POINT, S_POINT, R_MID_POINT, REC_L_MID_POINT, REC_S_POINT, REC_R_MID_POINT]

PER_TICK_ROT = -2 * math.pi / TICKS

model_dir = clip.directory('models')
os.chdir(model_dir)
img_dir = clip.directory('textures', 'item')

overrides = []


def get_rotation_matrix(angle):
    """ For background, https://en.wikipedia.org/wiki/Rotation_matrix
    rotation is clockwise in traditional descartes, and counterclockwise,
    if y goes down (as in picture coordinates)
    """
    return np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]])


def rotate(points, angle):
    """ Get coordinates of points rotated by a given angle counterclocwise

    Args:
        points (np.array): point coordinates shaped (n, 2)
        angle (float): counterclockwise rotation angle in radians
    Returns:
        np.array of new coordinates shaped (n, 2)
    """
    mid = np.array([IMG_MID, IMG_MID])
    relative_points = points - mid
    rot = get_rotation_matrix(angle)
    dot = relative_points.dot(rot)
    return dot + mid


for i in range(0, TICKS):
    img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), ImageColor.getrgb("#0000"))
    draw = ImageDraw.Draw(img)
    n, l, s, r, r_l, r_s, r_r = rotate(coords, i * PER_TICK_ROT)
    draw.polygon(list(map(tuple, (l, r, n))), fill=(ImageColor.getrgb("#f00f")))
    draw.polygon(list(map(tuple, (l, r, s))), fill=(ImageColor.getrgb("#000f")))
    img.save('%s/compass_%0*d.png' % (img_dir, TICK_DIGIT_COUNT, i))

    img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), ImageColor.getrgb("#0000"))
    draw = ImageDraw.Draw(img)
    draw.polygon(list(map(tuple, (l, r, n))), fill=(ImageColor.getrgb("#009295")))
    draw.polygon(list(map(tuple, (l, r, s))), fill=(ImageColor.getrgb("#29dfeb")))
    img.save('%s/recovery_compass_%0*d.png' % (img_dir, TICK_DIGIT_COUNT, i))

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
            "textures": {
                "layer0": "item/compass_%0*d" % (TICK_DIGIT_COUNT, i % TICKS)
            },
            "display": {
                "firstperson_righthand": {
                    "rotation": [-20, -35, 0],
                    "translation": FP_TRANSLATION,
                    "scale": FP_SCALE
                },
                "firstperson_lefthand": {
                    "rotation": [-20, -35, 0],
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


# noinspection PyUnusedLocal
def to_recovery(src, dst=None):
    old_text = open(src, 'r').read()
    new_text = old_text.replace('compass', 'recovery_compass')
    open(src.replace('compass', 'recovery_compass'), 'w').write(new_text)


# Recovery compass models are just modified compass ones
to_recovery("item/compass.json")
to_recovery("item/base_compass.json")
shutil.rmtree("item/recovery_compass", ignore_errors=True)
shutil.copytree("item/compass", "item/recovery_compass", copy_function=to_recovery)
