#!/usr/bin/env python

import ConfigParser
import json
import shutil

import Image
import os
import math


# Someday I should let the user specify an input config file on the command line... For now it's all hardcoded in here.


def to_color(color_spec):
    if color_spec[0] == '#':
        color_spec = color_spec[1:]
    return tuple(map(ord, color_spec.decode('hex')))


def clock_colors(config, section):
    return (
        to_color(config.get(section, 'face_color')),
        to_color(config.get(section, 'on_color')),
        to_color(config.get(section, 'off_color')),
    )


config = ConfigParser.SafeConfigParser()
config.read('clock_gen.cfg')

# The 'clock_in' describes the input image that defines the clock font, etc.
in_sec = 'clock_in'
digits_path = config.get(in_sec, 'digits_path')
digit_start = map(int, config.get(in_sec, 'digit_start').split())
assert len(digit_start) == 2
digit_size = map(int, config.get(in_sec, 'digit_size').split())
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
minutes_per_day = 60 * 24
tick_digit_cnt = int(math.ceil(math.log(ticks, 10)))

color_map = {}
for i in range(0, len(in_colors)):
    color_map[in_colors[i]] = out_colors[i]

digits_img = Image.open(digits_path).convert('RGB')
digit_pixels = digits_img.load()
for x in range(0, digits_img.size[0]):
    for y in range(0, digits_img.size[1]):
        digit_pixels[x, y] = color_map[digit_pixels[x, y]]

digit_imgs = {}
colon_img = None
for i in range(0, 10):
    x, y = (digit_start[0] + i * digit_size[0], digit_start[1])
    digit_imgs[str(i)] = digits_img.crop((x, y, x + digit_size[0], y + digit_size[1]))
    if i == 9:
        x += digit_size[0]
        colon_img = digits_img.crop((x, y, x + colon_width, y + digit_size[1]))


def clear_out_tree(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
    return dir_name


texture_dir = clear_out_tree('textures/items/clock')
model_dir = clear_out_tree('models/item/clock')

overrides = []

clock_width = 4 * digit_size[0] + colon_width

digit_pos = {}
x = (face_dim - clock_width) / 2
y = (face_dim - digit_size[1]) / 2
digit_pos[0] = (x, y)
x += digit_size[0]
digit_pos[1] = (x, y)
x += digit_size[0]
colon_pos = (x, y)
x += colon_width
digit_pos[2] = (x, y)
x += digit_size[0]
digit_pos[3] = (x, y)

blank_img = Image.new('RGB', (face_dim, face_dim), color=out_colors[0])
blank_img.paste(colon_img, colon_pos)


def write_digits(tick_img, num, at, draw_init_zero):
    num_str = '%02d' % num
    if num_str[0] != '0' or draw_init_zero:
        tick_img.paste(digit_imgs[num_str[0]], at)
    tick_img.paste(digit_imgs[num_str[1]], (at[0] + digit_size[0], at[1]))


for i in range(0, ticks):
    day_frac = i * tick_fraction
    total_minutes = round(minutes_per_day * day_frac)
    hrs = (int(total_minutes / 60) + 11) % 24
    mins = total_minutes % 60
    tick_img = blank_img.copy()
    write_digits(tick_img, hrs, digit_pos[0], False)
    write_digits(tick_img, mins, digit_pos[2], True)
    print "%d: %2d:%02d %f" % (i, hrs, mins, day_frac)

    name = 'clock_%0*d' % (tick_digit_cnt, i)
    texture = 'items/clock/%s' % name
    png_path = texture + '.png'
    model = 'item/clock/%s' % name
    json_path = model + '.json'
    overrides.append({"predicate": {"time": day_frac + tick_fraction / 2}, "model": model})
    tick_img.save('textures/%s' % png_path)
    with open('models/%s' % json_path, 'w') as f:
        json.dump({
            "parent": out_parent,
            "textures": {
                "layer0": texture
            }
        }, f, indent=4, sort_keys=True)

with open('models/item/clock.json', 'w') as f:
    json.dump({
        "parent": out_parent,
        "textures": {
            "layer0": "items/clock/clock_%0*d" % (tick_digit_cnt, 0)
        },
        "overrides": overrides
    }, f, indent=4, sort_keys=True)
