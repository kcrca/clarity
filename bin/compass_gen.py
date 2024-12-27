#!/usr/bin/env python3

# Generate the model files for the compass. There is an individual prop file for each displayed angle variation, and a
# primary model file that lists all those and when to show them. The variation in each file is how much to rotate the
# image.

__author__ = 'arnold'

import glob
import json
import math
import os

import numpy as np
from PIL import Image, ImageColor, ImageDraw

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

model_dir = clip.directory('models', 'item')
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
    n, l, s, r, r_l, r_s, r_r = rotate(coords, i * PER_TICK_ROT)


    def arrow_image(up_color, down_color):
        img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), ImageColor.getrgb("#0000"))
        draw = ImageDraw.Draw(img)
        draw.polygon(list(map(tuple, (l, r, n))), fill=(ImageColor.getrgb(up_color)))
        draw.polygon(list(map(tuple, (l, r, s))), fill=(ImageColor.getrgb(down_color)))
        return img


    arrow_image("#f00f", "#000f").save('%s/compass_%0*d.png' % (img_dir, TICK_DIGIT_COUNT, i))
    arrow_image("#009295", "#29dfeb").save('%s/recovery_compass_%0*d.png' % (img_dir, TICK_DIGIT_COUNT, i))
    with open(f'{model_dir}/compass_{i:02d}.json', 'w') as fp:
        json.dump({'parent': 'item/flat_clock', 'textures': {'layer0': f'item/compass_{i:02d}'}}, fp, indent=2)

    day_frac = i * TICK_FRACTION

    display = {
        "rotation": [-20, -35, 0],
        "translation": FP_TRANSLATION,
        "scale": FP_SCALE
    }


# noinspection PyUnusedLocal


# Recovery compass models are just modified compass ones
for f in glob.glob(f'{model_dir}/recovery_compass*.json'):
    os.remove(f)

for src in glob.glob(f'{model_dir}/compass*.json'):
    dst = src.replace('compass', 'recovery_compass')
    old_text = open(src, 'r').read()
    new_text = old_text.replace('compass', 'recovery_compass')
    open(src.replace('compass', 'recovery_compass'), 'w').write(new_text)
