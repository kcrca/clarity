#!/usr/bin/env python3
import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageColor
from PIL.ImageDraw import ImageDraw

import clip
from clip import has_transparency

top_dir = Path(clip.directory('top'))
src_dir = top_dir / 'default_resourcepack'
dst_dir = top_dir / 'call_out'
common = '/assets/minecraft'
copy_pat = re.compile('(textures|blockstates|models)')
with open(src_dir / 'version.json') as fp:
    version_info = json.load(fp)
version = version_info['pack_version']['resource']

dst_dir.mkdir(0o755, exist_ok=True)
this_dir = Path(__file__).parent

color = ImageColor.getrgb('#000000')
magenta = ImageColor.getrgb('#f800f8')
color_imgs = {}


def color_for(src_img):
    mode = 'RGBA' if has_transparency(src_img) else 'RGB'
    key = (mode, src_img.size)
    if key not in color_imgs:
        img = color_imgs[key] = Image.new(mode, src_img.size, color)
        drw = ImageDraw(img)
        sz = int(min(*src_img.size) / 2)
        if sz > 0:
            for x in range(0, src_img.size[0], sz):
                for y in range(0, src_img.size[1], sz):
                    if (x / sz + y / sz) % 2 == 0:
                        drw.rectangle(((x, y), (x + sz - 1, y + sz - 1)), fill=magenta)
    return color_imgs[key]


def colorify(src_path, dst_path, *, follow_symlinks=True):
    if not src_path.endswith('.png'):
        return shutil.copy2(src_path, dst_path, follow_symlinks=follow_symlinks)
    src_img = Image.open(src_path)
    has_alpha = has_transparency(src_img)
    src_img = src_img.convert('LA' if has_alpha else 'L').convert('RGBA' if has_alpha else 'RGB')
    colored_img = color_for(src_img)
    mod_img = Image.blend(src_img, colored_img, 0.5)
    if has_alpha:
        _, _, _, a = src_img.split()
        r, g, b, _ = mod_img.split()
        mod_img = Image.merge('RGBA', (r, g, b, a))
    mod_img.save(dst_path)


def call_out(dst_dir, full):
    def should_ignore(dir, files):
        def files_and(*args):
            return list(filter(lambda x: Path(src_dir / dir / x).is_dir() and x not in args, files))

        if dir == str(src_dir):
            return files_and('assets')
        if dir.endswith('/assets'):
            # I don't know what this does, but it confuses minecraft
            return files_and('minecraft') + ['.mcassetsroot']
        elif dir.endswith('assets/minecraft'):
            if full:
                return files_and('textures')
            return files_and('textures', 'models', 'blockstates')
        exclude = []
        if dir.endswith('/assets/minecraft/textures'):
            exclude.append('font')
            exclude.extend(filter(lambda x: full != (x in ('colormap', 'gui', 'misc', 'environment')), files))
        return exclude

    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir, copy_function=colorify, ignore=should_ignore)
    icon = this_dir / ('call_out_all.png' if full else 'call_out.png')
    shutil.copy2(icon, dst_dir / 'pack.png')
    thumb = Image.open(icon)
    thumb.thumbnail((64, 64), Image.Resampling.LANCZOS)
    thumb.save(dst_dir / 'pack_thumb.png')
    desc = 'Call out %s textures not in any pack (except fonts) by making them bright green.' % (
        'remaining' if full else 'most')
    with open(dst_dir / 'pack.mcmeta', 'w') as fp:
        json.dump({'pack': {'pack_format': version, 'description': desc}}, fp, indent=2)
        fp.write('\n')


call_out(dst_dir, False)
call_out(Path(str(dst_dir) + "_all"), True)
