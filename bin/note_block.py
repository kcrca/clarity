#!/usr/bin/env python3

# This program generates the item images for the daylight detector. It reads the model files
# for each detector state, grabs its block image, and pastes that into the image file for the item. This creates an
# animation with a frame per state. (This is only required for the daylight detector because the daylight detector
# inverted is never in an "item" state, it only exists in the real world as a modified daylight detector.)
#
# The creation of the .mcmeta file is left to the user.

from PIL import ImageOps, ImageColor

from clip import *


def colorize(img, color_hex):
    color = ImageColor.getcolor("#%06xff" % color_hex, 'RGBA')
    new_img = img.copy()
    pixels = new_img.load()
    for x in range(0, img.size[0]):
        for y in range(0, img.size[1]):
            if pixels[x, y][3] != 0:
                pixels[x, y] = color
    return new_img


SIZE = 40
LINE_POS = 28
NOTE_POS = 16
ON_COLOR = 0xe2b398

model_src_path = os.path.join(directory('models'), 'block', 'note_block/note_block_00.json')
model_src = open(model_src_path).read()

blocks = os.path.join(directory('textures'), 'block')

names_src_path = os.path.join(blocks, 'note_block_names.png')
names_img = Image.open(names_src_path).convert('RGBA')

staff_img = Image.open(os.path.join(blocks, 'note_block_staff.png')).convert('RGBA')
notation_img = Image.open(os.path.join(blocks, 'note_block_note.png')).convert('RGBA')
flat = notation_img.crop((0, 0, NOTE_POS, SIZE))
note = notation_img.crop((NOTE_POS, 0, LINE_POS, SIZE))
line = notation_img.crop((LINE_POS, 0, SIZE, SIZE))
note_on = colorize(note, ON_COLOR)
flat_on = colorize(flat, ON_COLOR)
height = 0
was_flat = False
note_adj = 0
flat_adj = 0
no_flats = (6, 11, 18, 23)

for i in range(0, 25):
    img = staff_img.copy()
    name_img = names_img.crop((4, i * 6, 12, (i + 1) * 6))
    img.paste(name_img, (3, 31), name_img)
    if not was_flat:
        height += 2
    if i < 4 or i > 22:
        adj = int((height + (2 if i < 4 else 0)) / 4) * 4
        img.paste(line, (14, 8 - adj), line)
    if i == 13:
        note = ImageOps.flip(note)
        note_on = ImageOps.flip(note_on)
        note_adj = 14
        flat_adj = 5
    img_on = img.copy()

    note_pos = (16, 8 - height + note_adj)
    img.paste(note, note_pos, note)
    img_on.paste(note_on, note_pos, note_on)

    if i not in no_flats and not was_flat:
        flat_pos = (0, (8 - height + flat_adj))
        img.paste(flat, flat_pos, flat)
        img_on.paste(flat_on, flat_pos, flat_on)
        was_flat = True
    else:
        was_flat = False

    num = '%02d' % i
    img_path = names_src_path.replace('_names', '_' + num)
    img.convert('RGB').save(img_path, optimize=True)
    img_on.convert('RGB').save(img_path.replace('.png', '_on.png'), optimize=True)

    model = model_src.replace('00', num)
    model_on = model_src.replace('00', num + '_on')
    open(model_src_path.replace('00', num), 'w').write(model)
    open(model_src_path.replace('00', num + '_on'), 'w').write(model_on)
