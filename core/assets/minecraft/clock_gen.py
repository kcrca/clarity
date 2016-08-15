#!/usr/bin/env python

import ConfigParser
import json
import Image
import glob
import os
import math


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


in_sec = 'clock_in'
in_defaults = {
    'digits_path': 'textures/items/clock_font.png',
    'digit_start': '0 0',
    'digit_size': '7 11',
    'colon_width': '2',
    'face_color': '#ffffff',
    'on_color': '#ff0000',
    'off_color': '#777777',
}
config = ConfigParser.SafeConfigParser(in_defaults)
config.read('clock_gen.cfg')

if not config.has_section(in_sec):
    config.add_section(in_sec)
digits_path = config.get(in_sec, 'digits_path')
digit_start = map(int, config.get(in_sec, 'digit_start').split())
assert len(digit_start) == 2
digit_size = map(int, config.get(in_sec, 'digit_size').split())
assert len(digit_size) == 2
colon_width = config.getint(in_sec, 'colon_width')
in_colors = clock_colors(config, in_sec)

out_sec = 'clock_out'
out_defaults = {
    'ticks': '1440',
    'face_color': '#000000',
    'on_color': '#00ff00',
    'off_color': '#003300',
}
# We cannot change the defaults for the parser, so we have to create a new parser
config = ConfigParser.SafeConfigParser(out_defaults)
config.read('clock_gen.cfg')
if not config.has_section(out_sec):
    config.add_section(out_sec)
ticks = config.getint(out_sec, 'ticks')
out_colors = clock_colors(config, out_sec)

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

pass
for f in glob.glob('textures/items/clock_[0-9]*.png'):
    os.remove(f)
for f in glob.glob('models/item/clock_[0-9]*.json'):
    os.remove(f)

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
    total_minutes = minutes_per_day * day_frac
    hrs = (int(total_minutes / 60) + 6) % 24
    mins = total_minutes % 60
    tick_img = blank_img.copy()
    write_digits(tick_img, hrs, digit_pos[0], False)
    write_digits(tick_img, mins, digit_pos[2], True)

    name = 'clock_%0*d' % (tick_digit_cnt, i)
    texture = 'items/%s' % name
    png_path = texture + '.png'
    model = 'item/%s' % name
    json_path = 'item/%s.json' % name
    overrides.append({"predicate": {"time": day_frac}, "model": model})
    tick_img.save('textures/%s' % png_path)
    with open('models/%s' % json_path, 'w') as f:
        json.dump({
            "parent": "item/generated",
            "textures": {
                "layer0": texture
            }
        }, f, indent=4, sort_keys=True)

with open('models/item/clock.json', 'w') as f:
    json.dump({
        "parent": "item/generated",
        "textures": {
            "layer0": "items/clock_%0*d" % (tick_digit_cnt, 0)
        },
        "overrides": overrides
    }, f, indent=4, sort_keys=True)
