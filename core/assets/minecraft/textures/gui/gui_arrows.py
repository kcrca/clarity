#!/usr/bin/env python
import ConfigParser
import os
import re
import shutil
from collections import defaultdict

from PIL import Image
from PIL import ImageDraw
from PIL import ImageColor
import numpy

desc_re = re.compile(r'(large)?_?(.*)_(.*)@(\d+),(\d+)')
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
    img = Image.open('container/parts/arrow_%s.png' % which).convert('RGBA')
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
        left = left_arrows(size, ('norm',))
        left.update(left_arrows(hover, ('hover',)))
    else:
        left = left_arrows(size)

    up = generate_arrows('up', left, Image.ROTATE_270)
    right = generate_arrows('right', left, Image.FLIP_LEFT_RIGHT)
    down = generate_arrows('down', up, Image.FLIP_TOP_BOTTOM)
    return {'left': left, 'right': right, 'up': up, 'down': down}


debug_nums = defaultdict(lambda: 0)
tmpdir = '/tmp/p'
shutil.rmtree(tmpdir)
os.makedirs(tmpdir)


def debug_image(panel_name, panel):
    debug_nums[panel_name] += 1
    panel.save('%s/%s%d.png' % (tmpdir, os.path.basename(panel_name), debug_nums[panel_name]))


config = ConfigParser.SafeConfigParser()
config.read('gui_arrows.cfg')

barred_arrows = config.getboolean('settings', 'barred_arrows')

arrows = {
    'small': build_arrows('small'),
    'large': build_arrows('large'),
    # 'large': build_arrows('large_norm', 'large_hover'),
}

panels = config.items('files')

for panel_name, part_str in panels:
    path = '%s.png' % panel_name
    panel = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(panel)

    parts = part_str.split()

    debug_image(panel_name, panel)
    for desc in parts:
        m = dim_re.match(desc)
        if m:
            space = map(lambda s: int(s), m.groups())
            continue
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
            debug_image(panel_name, panel)
            x += space[0]
    panel.save(path)
