#!/usr/bin/env python3
import glob
import os
import sys
import javaproperties

__author__ = 'arnold'

import random
import json
import clip

from PIL import Image
from PIL import ImageDraw

NUM_BLOCKS = 20

if len(sys.argv) == 1:
    print("Not regenerating without an argument")
    sys.exit(0)


def remove_all(pat):
    for p in glob.glob(pat):
        os.remove(p)


def shelf_texture(i):
    return 'bookshelf_%02d' % i


textures = clip.directory('textures', 'block')
models = clip.directory('models', 'block')
books_png = os.path.join(textures, 'books.png')
continuity = clip.directory('top', 'continuity.repack', 'override', 'assets', 'minecraft', 'textures', 'block')
connectivity = clip.directory('top', 'connectivity.repack', 'override', 'assets', 'minecraft', 'optifine', 'ctm', 'bookshelf')
books_img = Image.open(books_png)
books_pixel = books_img.load()

# Break up the books into individual book images
w, h = books_img.size
cur_color = books_pixel[0, h - 1]
books = []
start_x = 0
for x in range(0, w):
    if books_pixel[x, h - 1] != cur_color:
        book_img = books_img.crop((start_x, 0, x, h))
        books.append(book_img)
        start_x = x
        cur_color = books_pixel[start_x, h - 1]



def create_shelf(start, width, avoid, avail):
    chosen = []
    left = width
    while left > 0:
        choices = [x for x in avail if x.size[0] <= left]
        if len(choices) == 0:
            choices = [x for x in avoid if x.size[0] <= left]
            # better to repeat than have no choices (but avoid what's already in)
            for x in chosen:
                try:
                    choices.remove(x)
                except ValueError:
                    pass
        b = choices[random.randint(0, len(choices) - 1)]
        chosen.append(b)
        left -= b.size[0]
        if b in avail:
            avoid.append(b)
            avail.remove(b)
            if len(avoid) >= len(books) / 2:
                avail.append(avoid[0])
                avoid = avoid[1:]
    random.shuffle(chosen)
    x = 0
    shelf = Image.new('RGB', (16, 16), clip.hex_to_rgba('b8945f', -1))
    draw = ImageDraw.Draw(shelf)
    draw.rectangle((start, 1, width + start - 1, 14), fill=clip.hex_to_rgba('3a2d1a', -1))
    for img in chosen:
        clip.alpha_composite(shelf, img, (x + start, 1))
        x += img.size[0]
    return shelf


def bookshelf_for_pack(start, width, dir, prefix=''):
    os.makedirs(dir, exist_ok=True)
    remove_all(os.path.join(dir, '%s_[0-9]*.png' % prefix))
    avoid = []
    shelves = []
    avail = list(books)
    for i in range(0, NUM_BLOCKS):
        shelf = create_shelf(start, width, avoid, avail)
        shelves.append(shelf)
        shelf.save(os.path.join(dir, '%s_%02d.png' % (prefix, i)))


# Do the clarity (bordered) shelves.
bookshelf_for_pack(1, 14, textures, 'bookshelf')

# Do the continuity (unbordered) shelves.
bookshelf_for_pack(0, 16, continuity, 'bookshelf')

# Do the connectivity shelves.
bookshelf_for_pack(1, 15, connectivity, '0')
bookshelf_for_pack(0, 16, connectivity, '1')
bookshelf_for_pack(0, 15, connectivity, '2')
bookshelf_for_pack(1, 14, connectivity, '3')

dirs = ('north', 'east', 'west', 'south')
shelf_nums = list(range(0, NUM_BLOCKS))

remove_all(os.path.join(models, 'bookshelf_[0-9]*.json'))
blockstate = {'variants': {'': []}}
for i in range(0, NUM_BLOCKS):
    model = {
        'parent': 'minecraft:block/cube',
        'textures': {
            'particle': 'minecraft:block/bookshelf_00',
            'up': 'minecraft:block/oak_planks',
            'down': 'minecraft:block/oak_planks'
        }
    }
    random.shuffle(shelf_nums)
    for j, d in enumerate(dirs):
        model['textures'][d] = 'minecraft:block/' + shelf_texture(shelf_nums[j])
    model_name = shelf_texture(i)
    with open(os.path.join(models, model_name) + '.json', 'w') as f:
        json.dump(model, f, indent=2, sort_keys=True)
    blockstate['variants'][''].append({'model': 'block/%s' % model_name})

with open(os.path.join(clip.directory('blockstates'), 'bookshelf.json'), 'w') as f:
    json.dump(blockstate, f, indent=2, sort_keys=True)

ctm_props = {
    'matchBlocks': 'bookshelf',
    'method': 'horizontal',
    'faces': 'sides',
}
for i in range(0, NUM_BLOCKS):
    ctm_props['tiles'] = ' '.join(('%d_%02d' % (t, i)) for t in range(0, 4))
    with open(os.path.join(connectivity, 'bookshelf_%02d.properties' % i), 'w') as fp:
        javaproperties.dump(ctm_props, fp)
