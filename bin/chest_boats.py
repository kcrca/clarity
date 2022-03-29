import glob
import os

from PIL import Image

import clip

entity_dir = clip.directory('textures', 'entity')
dir = entity_dir + '/chest_boat'
boat_dir = entity_dir + '/boat'
os.chdir(dir)

chest = Image.open('chest.png').convert('RGBA')
for chest_boat in glob.glob('*.png'):
    if chest_boat != 'chest.png':
        boat = Image.open(boat_dir + "/" + chest_boat).convert('RGBA')
        img = chest.copy()
        img.paste(boat, mask=boat)
        img.save(chest_boat)
