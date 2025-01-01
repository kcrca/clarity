#!/usr/bin/env python3

__author__ = 'arnold'

import configparser
import copy
import glob
import json
import math
import os
import shutil

from PIL import Image, ImageColor
from PIL.ImageDraw import ImageDraw

import clip


# Someday I should let the user specify an input config file on the command line... For now it's all hardcoded in here.


def clock_colors(config, section):
    return (
        clip.hex_to_rgba(config.get(section, 'face_color')),
        clip.hex_to_rgba(config.get(section, 'on_color')),
        clip.hex_to_rgba(config.get(section, 'off_color')),
    )


config = configparser.ConfigParser()
config.read(clip.directory('config', 'clock_gen.cfg'))

os.chdir(clip.directory('minecraft'))

# The 'clock_in' describes the input image that defines the clock font, etc.
in_sec = 'clock_in'
digits_path = __file__.replace('.py', '.png')
digit_start = list(map(int, config.get(in_sec, 'digit_start').split()))
assert len(digit_start) == 2
digit_size = list(map(int, config.get(in_sec, 'digit_size').split()))
assert len(digit_size) == 2
colon_width = config.getint(in_sec, 'colon_width')
in_colors = clock_colors(config, in_sec)

# The clock_out section is how the generated clock will look
out_sec = 'clock_out'
ticks = config.getint(out_sec, 'ticks')
out_colors = clock_colors(config, out_sec)
out_parent = config.get(out_sec, 'parent')

face_dim = int(round(math.pow(2, math.ceil(math.log(4 * digit_size[0] + colon_width, 2)))))

tick_fraction = 1.0 / ticks
half_tick_fraction = tick_fraction / 2
minutes_per_day = 60 * 24
tick_digit_cnt = int(math.ceil(math.log(ticks, 10)))

color_map = {}
for i in range(0, len(in_colors)):
    color_map[in_colors[i]] = out_colors[i]

digits_img = Image.open(digits_path).convert('RGBA')
digit_pixels = digits_img.load()
for x in range(0, digits_img.size[0]):
    for y in range(0, digits_img.size[1]):
        digit_pixels[x, y] = color_map[digit_pixels[x, y]]

digit_imgs = {}
colon_img = None
for i in range(0, 11):
    x, y = (digit_start[0] + i * digit_size[0], digit_start[1])
    name = str(i) if i < 10 else '?'
    digit_imgs[name] = digits_img.crop((x, y, x + digit_size[0], y + digit_size[1]))
    if i == 10:
        x += digit_size[0]
        colon_img = digits_img.crop((x, y, x + colon_width, y + digit_size[1]))


def clear_out_tree(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
    return dir_name


texture_dir = clear_out_tree('textures/item/clock')
model_dir = clear_out_tree('models/item/clock')

clock_width = 4 * digit_size[0] + colon_width

digit_pos = {}
x = int((face_dim - clock_width) / 2)
y = int((face_dim - digit_size[1]) / 2)
digit_pos[0] = (x, y)
x += digit_size[0]
digit_pos[1] = (x, y)
x += digit_size[0]
colon_pos = (x, y)
x += colon_width
digit_pos[2] = (x, y)
x += digit_size[0]
digit_pos[3] = (x, y)

blank_img = Image.new('RGBA', (face_dim, face_dim), color=out_colors[0])
blank_img.paste(colon_img, colon_pos)


def write_digits(tick_img, num_str, at, draw_init_zero):
    if num_str[0] != '0' or draw_init_zero:
        tick_img.paste(digit_imgs[num_str[0]], at)
    tick_img.paste(digit_imgs[num_str[1]], (at[0] + digit_size[0], at[1]))


fixed_overrides = []

for i in range(-1, ticks + 1):
    day_frac = i * tick_fraction
    total_minutes = round(minutes_per_day * day_frac)
    hrs = (int(total_minutes / 60) + 12) % 24
    mins = total_minutes % 60

    name = 'fixed_%0*d' % (tick_digit_cnt, i % ticks) if i >= 0 else 'clock_unk'
    texture = 'item/clock/%s' % name
    png_path = texture + '.png'
    model = 'item/clock/%s' % name
    json_path = model + '.json'
    if i >= 0:
        at_time_frac = day_frac
        if i > 0:
            at_time_frac -= half_tick_fraction
        fixed_overrides.append({
            "model": {
                "type": "minecraft:model",
                "model": f"minecraft:item/clock/fixed_{i % ticks:03d}"
            },
            "threshold": at_time_frac
        })
    if i < ticks:
        # no need to write the image when i >= ticks since we already have
        tick_img = blank_img.copy()
        if i < 0:
            write_digits(tick_img, '??', digit_pos[0], False)
            write_digits(tick_img, '??', digit_pos[2], True)
        else:
            write_digits(tick_img, '%02d' % hrs, digit_pos[0], False)
            write_digits(tick_img, '%02d' % mins, digit_pos[2], True)
        tick_img.save('textures/%s' % png_path, optimize=True)

    path = 'models/%s' % json_path
    with open(path, 'w') as f:
        json.dump({
            "parent": out_parent,
            "textures": {
                "layer0": texture
            }
        }, f, indent=4, sort_keys=True)

# Now create the non-fixed variants of everything
for f in glob.glob(f'{model_dir}/fixed_*'):
    with open(f) as src:
        txt = src.read()
        with open(f.replace('fixed_', 'clock_'), 'w') as dst:
            dst.write(txt.replace('fixed_', 'clock_'))

one = digit_imgs['1']
data = one.getdata()
left = 1000
for i in range(len(data)):
    px = data[i]
    if px[3] != 0:
        left = min(left, i % one.size[0])
half = int(left / 2)

for f in glob.glob(f'{texture_dir}/*.png'):
    with Image.open(f) as src:
        dst = Image.new(src.mode, src.size, ImageColor.getrgb('#0000'))
        draw = ImageDraw(dst)
        bg = ImageColor.getrgb('#202020')
        draw.rectangle((0, digit_pos[0][1] - 2, dst.size[0], digit_pos[0][1] + digit_size[1] + 1), fill=bg)

        src_pos = (left, digit_pos[0][1], digit_pos[3][0] + digit_size[0], digit_pos[3][1] + digit_size[1])
        time = src.crop(src_pos)
        dst.paste(time, (half, src_pos[1]), time)
        dst.save(f.replace('fixed_', 'clock_'))

fixed_display = {
    "model": {
        "type": "minecraft:select",
        "property": "minecraft:context_dimension",
        "cases": [{
            "model": {
                "type": "minecraft:range_dispatch",
                "entries": fixed_overrides,
                "property": "minecraft:time",
                "scale": 1.0,
                "source": "daytime",
                "wobble": False,
            },
            "when": "minecraft:overworld"
        }],
        "fallback": {
            "model": "item/clock/clock_unk",
            "type": "model",
        },
    }
}
clock_display = copy.deepcopy(fixed_display['model']['cases'][0]['model'])
for e in clock_display['entries']:
    e['model']['model'] = e['model']['model'].replace('fixed_', 'clock_')
model = {
    "model": {
        "type": "minecraft:select",
        "property": "minecraft:display_context",
        "cases": [{
            "when": "fixed",
            "model": fixed_display['model']
        }],
        "fallback": clock_display
    }
}
with open('items/clock.json', 'w') as f:
    json.dump(model, f, indent=4, sort_keys=True)
