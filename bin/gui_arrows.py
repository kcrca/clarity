#!/usr/bin/env python3

__author__ = 'arnold'

import configparser
import os
import re
import shutil
from collections import defaultdict

import numpy
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL.Image import Transpose

import clip

desc_re = re.compile(r'(large)?_?(.*)_(.*)@(\d+),(\d+)')
dim_re = re.compile(r'(\d+)x(\d+)')

gui_dir = clip.directory('textures', 'gui')


def to_colors(which):
    strs = config.get('settings', which).split()
    return {
        'norm': ImageColor.getcolor(strs[0], 'RGBA'),
        'hover': ImageColor.getcolor(strs[1], 'RGBA'),
        'barred': ImageColor.getcolor(strs[2], 'RGBA'),
    }


def colored_arrow(img, colors, which):
    if not barred_arrows and which == 'barred':
        return Image.new("RGBA", img.size)

    data = numpy.array(img)
    _, _, _, alpha = data.T
    image_areas = alpha != 0
    data[...][image_areas.T] = colors[which]
    arrow = Image.fromarray(data)
    return arrow


def left_arrows(which, types=('norm', 'hover')):
    img = Image.open(os.path.join(gui_dir, 'container/parts/arrow_%s.png' % which)).convert('RGBA')
    try:
        barred_path = os.path.join(gui_dir, 'container/parts/arrow_%s_bar.png' % which)
        bar = Image.open(barred_path).convert('RGBA')
        types += ('barred',)
    except IOError as e:
        bar = None
    colors = to_colors(which)
    arrows = {}
    for which in types:
        arrows[which] = colored_arrow(img, colors, which)
    if bar:
        arrows['barred'] = Image.alpha_composite(arrows['barred'], bar)
    return arrows


def generate_arrows(which, src_arrows, transform):
    imgs = {}
    for a in src_arrows:
        imgs[a] = src_arrows[a].transpose(transform)
    return imgs


def build_arrows(size, hover=None):
    if hover:
        left = left_arrows(size, ('norm',))
        left.update(left_arrows(hover, ('hover',)))
    else:
        left = left_arrows(size)

    up = generate_arrows('up', left, Transpose.ROTATE_270)
    right = generate_arrows('right', left, Transpose.FLIP_LEFT_RIGHT)
    down = generate_arrows('down', up, Transpose.FLIP_TOP_BOTTOM)
    return {'left': left, 'right': right, 'up': up, 'down': down}


DEBUG = False
debug_nums = defaultdict(lambda: 0)
tmpdir = '/tmp/p'
if DEBUG:
    shutil.rmtree(tmpdir)
    os.makedirs(tmpdir)


def debug_image(panel_name, panel):
    if DEBUG:
        debug_nums[panel_name] += 1
        panel.save('%s/%s%d.png' % (tmpdir, os.path.basename(panel_name), debug_nums[panel_name]), optimize=True)


config = configparser.ConfigParser()
config.read(clip.directory('config', 'gui_arrows.cfg'))

barred_arrows = config.getboolean('settings', 'barred_arrows')

arrows = {
    'small': build_arrows('small'),
    'large': build_arrows('large'),
    # 'large': build_arrows('large_norm', 'large_hover'),
}

panels = config.items('files')

for panel_name, part_str in panels:
    path = os.path.join(gui_dir, '%s.png' % panel_name)
    panel = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(panel)

    parts = part_str.split()

    debug_image(panel_name, panel)
    for desc in parts:
        m = dim_re.match(desc)
        if m:
            space = [int(s) for s in m.groups()]
            continue
        m = desc_re.match(desc)
        if not m:
            print('%s: cannot parse desc: %s' % (panel_name, desc))
            continue
        size, towards, which, x_pos_str, y_pos_str = m.groups()
        if not size:
            size = 'small'
        x, y = [int(s) for s in (x_pos_str, y_pos_str)]
        bg = panel.getpixel((x, y))
        types = (which,)
        if which == 'all':
            types = ('norm', 'hover', 'barred')
        elif which == 'both':
            types = ('norm', 'hover')
        for type in types:
            draw.rectangle((x, y, x + space[0], y + space[1]), fill=bg)
            arrow = arrows[size][towards][type]
            dim = arrow.size
            delta = [int((space[i] - dim[i]) / 2) for i in range(0, len(space))]
            clip.alpha_composite(panel, arrow, (x + delta[0], y + delta[1]))
            debug_image(panel_name, panel)
            x += space[0]
    panel.save(path)
