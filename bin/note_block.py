#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.

from clip import *
from PIL import ImageOps

model_src_path = os.path.join(directory('models'), 'block', 'note_block/note_block_00.json')
model_src = open(model_src_path).read()

blocks = os.path.join(directory('textures'), 'block')

names_src_path = os.path.join(blocks, 'note_block_names.png')
names_img = Image.open(names_src_path).convert('RGBA')

staff_img = Image.open(os.path.join(blocks, 'note_block_staff.png')).convert('RGBA')
notation_img = Image.open(os.path.join(blocks, 'note_block_note.png')).convert('RGBA')
flat_img = notation_img.crop((0, 0, 16, 40))
note_img = notation_img.crop((16, 0, 24, 40))
line_img = notation_img.crop((24, 0, 40, 40))
height = 0
was_flat = False
note_adj = 0
flat_adj = 0
no_flats = (6, 11, 18, 23)

for i in range(0, 25):
    img = staff_img.copy()
    name_img = names_img.crop((2, i * 6, 12, (i + 1) * 6))
    img.paste(name_img, (3, 31))
    if not was_flat:
        height += 2
    if i < 4 or i > 22:
        adj = int((height + (2 if i < 4 else 0)) / 4) * 4
        img.paste(line_img, (14, 8 - adj), line_img)
    if i == 12:
        note_img = ImageOps.flip(note_img)
        note_adj = 14
        flat_adj = 5
    img.paste(note_img, (16, 8 - height + note_adj), note_img)

    if i not in no_flats and not was_flat:
        img.paste(flat_img, (0, 8 - height + flat_adj), flat_img)
        was_flat = True
    else:
        was_flat = False

    num = '%02d' % i
    img.convert('RGB').save(names_src_path.replace('_names', '_' + num), optimize=True)

    model = model_src.replace('00', num)
    open(model_src_path.replace('00', num), 'w').write(model)
