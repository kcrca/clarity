import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageColor

import clip

top_dir = Path(clip.directory('top'))
src_dir = top_dir / 'default_resourcepack'
dst_dir = top_dir / 'call_out'
textures = str(src_dir / 'assets/minecraft/textures')

dst_dir.mkdir(0o755, exist_ok=True)

color = ImageColor.getrgb("#39FF14")
color_imgs = {}


def color_for(src_img):
    mode = 'RGBA' if has_transparency(src_img) else 'RGB'
    key = (mode, src_img.size)
    if key not in color_imgs:
        color_imgs[key] = Image.new(mode, src_img.size, color)
    return color_imgs[key]


def has_transparency(img):
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode[-1] == "A":
        return True

    return False


def colorify(src_path, dst_path, *, follow_symlinks=True):
    if not src_path.endswith('.png'):
        return shutil.copy2(src_path, dst_path, follow_symlinks=follow_symlinks)
    src_img = Image.open(src_path)
    orig_mode = src_img.mode
    has_alpha = has_transparency(src_img)
    src_img = src_img.convert('LA' if has_alpha else 'L').convert('RGBA' if has_alpha else 'RGB')
    colored_img = color_for(src_img)
    mod_img = Image.blend(src_img, colored_img, 0.5)
    if has_alpha:
        _, _, _, a = src_img.split()
        r, g, b, _ = mod_img.split()
        mod_img = Image.merge('RGBA', (r, g, b, a))
    if orig_mode != src_img.mode:
        mod_img = mod_img.convert(orig_mode)
    mod_img.save(dst_path)


def call_out(dst_dir, full):
    def should_ignore(dir, files):
        if dir != textures and textures.startswith(dir):
            def top_filter(file):
                path = Path(dir) / file
                return path.is_dir() and not textures.startswith(str(path))

            return list(filter(top_filter, files))
        if dir == textures:
            exclude = ['font'] + list(
                filter(lambda x: full != (x in ('colormap', 'gui', 'misc', 'environment')), files))
            return exclude
        return ()

    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir, copy_function=colorify, ignore=should_ignore)
    with open(dst_dir / 'pack.mcmeta', 'w') as fp:
        json.dump({'pack': {'pack_format': 18, 'description': 'Call out textures not in any pack'}}, fp, indent=2)


call_out(dst_dir, False)
call_out(Path(str(dst_dir) + "_all"), True)
