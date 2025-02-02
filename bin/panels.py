#!/usr/bin/env python3

# Generate the panels for the containers.

__author__ = 'arnold'

import configparser
import glob
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw

import clip

desc_re = re.compile(r'(.*)@(?:(\d+),(\d+)(?:~(-?\d+))?|(right|bottom))')
grid_re = re.compile(r'(\d+)(?:x(\d+))?')


def open_part(part):
    try:
        return Image.open('parts/%s' % part).convert("RGBA")
    except FileNotFoundError:
        return Image.open(mc_dir / ('parts/%s' % part)).convert("RGBA")


used_part_files = []
mc_dir = Path(clip.directory('textures', 'gui', 'container'))
slot = Image.open(mc_dir / 'parts/slot.png').convert("RGBA")
for dir in glob.glob(str(mc_dir).replace('minecraft', '*')):
    print('%s:' % dir)
    os.chdir(dir)
    if not Path('panels.cfg').exists():
        print('    Skipping')
        continue
    config = configparser.ConfigParser()
    config.read('panels.cfg')

    slot_width = slot_height = 18


    def config_color(cname):
        return clip.hex_to_rgba(config.get('basic', cname))


    bg_in = config_color('background_in')
    bg = config_color('background')
    font_color = config_color('font_color')
    font_size = config.getint('basic', 'font_size')
    basic = dict(config.items('basic'))

    panels = config.items('panels')

    digits = {}
    chars = Image.open(mc_dir / 'parts/digits.png').convert('RGBA')
    raw_font_size = int(chars.size[0] / 16)  # font glyphs are stored 16 to a row
    digit_row_top = 3 * raw_font_size
    for i in range(0, 10):
        x1 = i * raw_font_size
        y1 = digit_row_top
        x2 = x1 + raw_font_size
        y2 = y1 + raw_font_size
        digit = chars.crop((x1, y1, x2, y2)).convert('RGBA')
        if font_size != raw_font_size:
            digit.thumbnail((font_size, font_size), Image.Resampling.LANCZOS)
        digits[i] = digit

    for panels_desc, part_str in panels:
        for panel in panels_desc.split(','):
            output_path = '%s.png' % panel
            if re.match(r'^\.\./', output_path):
                print('    ' + output_path)
            # We remove any leading "../"s to make it possible to rework a file above
            # the 'container' dir.
            blank = re.sub(r'^(\.\./)+', '', output_path)
            input = open_part(blank)
            used_part_files.append(output_path)

            # Set the background
            if bg_in != bg:
                pixels = input.load()
                for x in range(0, input.size[0]):
                    for y in range(0, input.size[1]):
                        if pixels[x, y] == bg_in:
                            pixels[x, y] = bg
                input.save(blank, optimize=True)

            output = input.copy()
            draw = ImageDraw.Draw(output)
            x_size, y_size = output.size

            parts = part_str.split()

            print("    Generating %s" % panel)

            for desc in parts:
                m = desc_re.match(desc)
                if not m:
                    print('%s: cannot parse desc: %s' % (panel, desc))
                    continue
                part, x_pos_str, y_pos_str, rotation_str, relative = m.groups()

                if relative == 'right':
                    x_pos, y_pos = x_size, 0
                elif relative == 'bottom':
                    x_pos, y_pos = 0, y_size
                else:
                    x_pos, y_pos = int(x_pos_str), int(y_pos_str)
                rotation = float(rotation_str) if rotation_str else 0


                def handle_part(part):
                    while part in basic:
                        part = basic[part]
                        subparts = part.split()
                        if len(subparts) > 1:
                            for subpart in subparts:
                                handle_part(subpart)
                            return

                    m = grid_re.match(part)
                    if m:
                        x_count_str, y_count_str = m.groups()
                        if not y_count_str:
                            y_count_str = '1'
                        x_count, y_count = int(x_count_str), int(y_count_str)
                        if not y_count:
                            y_count = 1
                        for x in range(0, x_count):
                            slot_x = x_pos + x * slot_width
                            for y in range(0, y_count):
                                slot_y = y_pos + y * slot_width
                                pos = (slot_x, slot_y)
                                clip.alpha_composite(output, slot, pos, rotation)
                        used_part_files.append('slot.png')
                    elif part == 'numbers':
                        draw = ImageDraw.Draw(output)
                        for i in range(1, 10):
                            x = x_pos + (i - 1) * slot_width + font_size / 2 + 4
                            y = y_pos + slot_height + 1
                            draw.bitmap((x, y), digits[i], fill=font_color)
                        used_part_files.append('digits.png')
                    elif part.startswith("item/"):
                        part_img = Image.open('../../%s.png' % part).convert("RGBA")
                        pixels = part_img.load()
                        for x in range(0, part_img.size[0]):
                            for y in range(0, part_img.size[1]):
                                c = pixels[x, y]
                                if c[3] != 0:
                                    pixels[x, y] = (c[0], c[1], c[2], int(round(c[3] * 0.4)))
                        pos1 = (x_pos, y_pos)
                        clip.alpha_composite(output, part_img, pos1, rotation)
                    else:
                        part_img = open_part(part)
                        pos2 = (x_pos, y_pos)
                        clip.alpha_composite(output, part_img, pos2, rotation)
                        used_part_files.append(part)


                handle_part(part)

            output.save(output_path, 'PNG')

parts_files = [x for x in os.listdir(mc_dir / 'parts') if x[-4:] == '.png']
unused = set(parts_files) - set(used_part_files) - set('slot.png')

if len(unused) > 0:
    print("unused parts: %s" % ', '.join(unused))
