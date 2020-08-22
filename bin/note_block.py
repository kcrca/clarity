#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.
import copy
import json
import os

from PIL import Image
from clip import *

img_src_path = os.path.join(directory('textures'), 'block', 'note_block_notes.png')
img_src = Image.open(img_src_path).convert('RGB')
bg = img_src.load()[0, 0]
model_src_path = os.path.join(directory('models'), 'block', 'note_block/note_block_00.json')
model_src = json.load(open(model_src_path))

for i in range(0, 25):
    img = Image.new('RGB', (16, 16), bg)
    note_img = img_src.crop((1, i * 6, 12, (i + 1) * 6))
    img.paste(note_img, (0, 0))
    num = '%02d' % i
    img.save(img_src_path.replace('_notes', '_' + num))
    model = copy.deepcopy(model_src.copy())
    textures = model['textures']
    for k in textures:
        textures[k] = textures[k].replace('00', num)
    dump(model_src_path.replace('00', num), model)
