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
type_imgs = []
profession_imgs = []
for file in glob.glob("parts/*.png"):
    img = Image.open(file).convert("RGBA")
    if '/type' in file:
        type_imgs += (img,)
    else:
        profession_imgs += (img,)
        professions += (os.path.basename(file)[:-4],)

output_dir = '../../../mcpatcher/mob/villager/'
make_sure_path_exists(output_dir)
for i in range(0, len(professions)):
    prof_img = profession_imgs[i]
    prof = professions[i]
    n = 1
    for t in type_imgs:
        img = Image.alpha_composite(t, prof_img)
        path = prof + ('' if n == 1 else '%d' % n) + '.png'
        img.save(os.path.join(output_dir, path))
        # Save the canonical ones
        if i + 1 == n:
            img.save(prof + '.png')
        n += 1
