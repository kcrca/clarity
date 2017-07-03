#!/usr/bin/env python
import ConfigParser
import os
import re
from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
import numpy

desc_re = re.compile(r'(large_)?(.*)_(.*)@(\d+),(\d+)')
dim_re = re.compile(r'(\d+)x(\d+)')


# This composites an image onto another merging the alpha properly. This should
# be part of PIL, but I can't find it.
# From http://stackoverflow.com/questions/3374878/with-the-python-imaging
# -library-pil-how-does-one-compose-an-image-with-an-alp
def alpha_composite(output, image, pos, rotation=0):
    if rotation:
        size = image.size
        image = image.rotate(rotation, expand=1).resize(size, Image.ANTIALIAS)
    r, g, b, a = image.split()
    rgb = Image.merge("RGB", (r, g, b))
    mask = Image.merge("L", (a,))
    output.paste(rgb, pos, mask)


def to_colors(arrow_name):
    strs = config.get('settings', 'small').split()
    return {
        'norm': ImageColor.getcolor(strs[0], 'RGBA'),
        'hover': ImageColor.getcolor(strs[1], 'RGBA'),
        'barred': ImageColor.getcolor(strs[2], 'RGBA'),
    }


def colored_arrow(img, colors, which):
    data = numpy.array(img)
    _, _, _, alpha = data.T
    image_areas = alpha != 0
    data[...][image_areas.T] = colors[which]
    arrow = Image.fromarray(data)
    return arrow


def left_arrows(which):
    img = Image.open('container/parts/arrow_%s.png' % which).convert('RGBA')
    types = ('norm', 'hover')
    try:
        bar = Image.open('container/parts/arrow_%s_bar.png' % which).convert('RGBA')
        types += ('barred',)
    except:
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
        imgs = left_arrows(size)
        imgs.update(left_arrows(hover))
    else:
        imgs = left_arrows(size)

    return {
        'left': imgs,
        'right': generate_arrows('right', imgs, Image.FLIP_LEFT_RIGHT),
        'up': generate_arrows('up', imgs, Image.ROTATE_270),
        'down': generate_arrows('down', imgs, Image.ROTATE_90),
    }


config = ConfigParser.SafeConfigParser()
config.read('arrows.cfg')

arrows = {
    'small': build_arrows('small'),
    'large': build_arrows('large_norm', 'large_hover'),
}

panels = config.items('files')
for panel_name, part_str in panels:
    path = '%s.png' % panel_name
    panel = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(panel)

    parts = part_str.split()
    dimension_str = parts[0]
    parts = parts[1:]

    space = map(lambda s: int(s), dim_re.match(dimension_str).groups())

    i = 0
    panel.save('p%d.png' % i)
    i += 1
    for desc in parts:
        m = desc_re.match(desc)
        if not m:
            print '%s: cannot parse desc: %s' % (panel_name, desc)
            continue
        size, towards, which, x_pos_str, y_pos_str = m.groups()
        if not size:
            size = 'small'
        x, y = map(lambda s: int(s), (x_pos_str, y_pos_str))
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
            delta = map(lambda i: int((space[i] - dim[i]) / 2), range(0, len(space)))
            alpha_composite(panel, arrow, (x + delta[0], y + delta[1]))
            panel.save('p%d.png' % i)
            i += 1
            x += space[0]
