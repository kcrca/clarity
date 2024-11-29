#!/usr/bin/env python3
from pathlib import Path

from PIL import ImageColor

from clip import *


# This program generates the item images for the note blocks. We use flats instead of sharps because they are narrower;
# the sharps just look too big.

def colorize(img, color_hex):
    color = ImageColor.getcolor("#%06xff" % color_hex, 'RGBA')
    new_img = img.copy()
    pixels = new_img.load()
    for x in range(0, img.size[0]):
        for y in range(0, img.size[1]):
            if pixels[x, y][3] != 0:
                pixels[x, y] = color
    return new_img


LINE_POS_SRC_X = 46
NOTE1_POS_SRC_X = 27
FLAT_POS_SRC_X = 23
ON_COLOR = 0xe2b398
HEIGHT_BASE = 15
NOTE_WIDTH = 19

LINE_POS_X = 23

model_src_path = os.path.join(directory('models'), 'block', 'note_block/note_block_00.json')
model_src = open(model_src_path).read()

blocks = os.path.join(directory('textures'), 'block')

names_src_path = os.path.join(Path(__file__).parent / 'note_block_names.png')
names_img = Image.open(names_src_path).convert('RGBA')
names_dst_path = str(Path(blocks) / 'note_block')

staff_img = Image.open(os.path.join(blocks, 'note_block_staff.png')).convert('RGBA')
size = staff_img.size[0]
notation_img = Image.open(os.path.join(blocks, 'note_block_note.png')).convert('RGBA')
flat = notation_img.crop((FLAT_POS_SRC_X, 0, NOTE1_POS_SRC_X, size))
note1 = notation_img.crop((NOTE1_POS_SRC_X, 0, NOTE1_POS_SRC_X + NOTE_WIDTH, size))
note2 = notation_img.crop((0, 0, NOTE_WIDTH, size))
line = notation_img.crop((LINE_POS_SRC_X, 0, size, size))
note_on1 = colorize(note1, ON_COLOR)
note_on2 = colorize(note2, ON_COLOR)
flat_on = colorize(flat, ON_COLOR)
height = -1
was_flat = False
note_adj = 0
flat_adj = 0
no_flats = (6, 11, 18, 23)
note = note1
note_on = note_on1

for i in range(0, 25):
    img = staff_img.copy()
    name_img = names_img.crop((3, i * 8, 13, (i + 1) * 8))
    img.paste(name_img, (5, size - 6 - name_img.size[1]), name_img)

    # Adjust for when the note flips upside down
    if i == 16:
        note = note2
        note_on = note_on2
        note_adj = 17
        flat_adj = 0

    # Place the below-clef lines
    if i < 7:
        img.paste(line, (LINE_POS_X, HEIGHT_BASE - 11), line)
        if i < 4:
            img.paste(line, (LINE_POS_X, HEIGHT_BASE - 5), line)
    img_on = img.copy()

    # Change the height when needed, then place the note itself
    if not was_flat:
        height += 3
    note_pos = (NOTE1_POS_SRC_X, HEIGHT_BASE - height + note_adj)
    img.paste(note, note_pos, note)
    img_on.paste(note_on, note_pos, note_on)

    if i not in no_flats and not was_flat:
        flat_pos = (FLAT_POS_SRC_X, (HEIGHT_BASE - height + flat_adj))
        img.paste(flat, flat_pos, flat)
        img_on.paste(flat_on, flat_pos, flat_on)
        was_flat = True
    else:
        was_flat = False

    num = '%02d' % i
    img_path = f'{names_dst_path}_{num}.png'
    img.convert('RGB').save(img_path, optimize=True)
    img_on.convert('RGB').save(img_path.replace('.png', '_on.png'), optimize=True)

    model = model_src.replace('00', num)
    model_on = model_src.replace('00', num + '_on')
    open(model_src_path.replace('00', num), 'w').write(model)
    open(model_src_path.replace('00', num + '_on'), 'w').write(model_on)
