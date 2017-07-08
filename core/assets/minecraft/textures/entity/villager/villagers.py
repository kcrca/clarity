#!/usr/bin/env python
import ConfigParser
import glob
import os
import re
import shutil
from collections import defaultdict

import errno
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
import numpy


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


orig_dir = os.getcwd()

professions = []
under_imgs = []
over_imgs = []
profession_imgs = []
for file in glob.glob("parts/*.png"):
    img = Image.open(file).convert("RGBA")
    if 'under' in file:
        under_imgs += (img,)
    elif 'over' in file:
        over_imgs += (img,)
    else:
        profession_imgs += (img,)
        professions += (os.path.basename(file)[:-4],)

output_dir = '../../../mcpatcher/mob/villager/'
make_sure_path_exists(output_dir)
for i in range(0, len(professions)):
    prof_img = profession_imgs[i]
    prof = professions[i]
    variant = 1
    for j in range(0, len(under_imgs)):
        img = Image.alpha_composite(under_imgs[j], prof_img)
        img = Image.alpha_composite(img, over_imgs[j])
        path = prof + ('' if variant == 1 else '%d' % variant) + '.png'
        img.save(os.path.join(output_dir, path))
        # Save the canonical ones
        if i + 1 == variant:
            img.save(prof + '.png')
        variant += 1
