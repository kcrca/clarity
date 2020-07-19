#!/usr/bin/env python
import glob
import os
import sys

__author__ = 'arnold'

import random
import json
import clip

from PIL import Image
from PIL import ImageDraw

if len(sys.argv) == 1:
    print "Not regenerating without an argument"
    sys.exit(0)


def remove_all(pat):
    for p in glob.glob(pat):
        os.remove(p)


def shelf_texture(i):
    return 'bookshelf_%02d' % i


textures = clip.directory('textures', 'block')
models = clip.directory('models', 'block')
books_png = os.path.join(textures, 'books.png')
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

remove_all(os.path.join(textures, 'bookshelf_[0-9]*.png'))
avoid = []
avail = list(books)
shelves = []
for i in range(0, 20):
    left = 14
    chosen = []
    while left > 0:
        choices = filter(lambda x: x.size[0] <= left, avail)
        if len(choices) == 0:
            # better to repeat than have no choices (but avoid what's already in)
            choices = filter(lambda x: x.size[0] <= left, set(avoid) - set(chosen))
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
    draw.rectangle((1, 1, 14, 14), fill=clip.hex_to_rgba('3a2d1a', -1))
    for img in chosen:
        clip.alpha_composite(shelf, img, (x + 1, 1))
        x += img.size[0]

    shelves.append(shelf)
    shelf.save(os.path.join(textures, 'bookshelf_%02d.png' % i))

dirs = ('north', 'east', 'west', 'south')
shelf_nums = range(0, len(shelves))

remove_all(os.path.join(models, 'bookshelf_[0-9]*.json'))
blockstate = {'variants': {'': []}}
for i in range(0, 19):  
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
