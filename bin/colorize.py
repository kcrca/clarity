#!/usr/bin/env python3
import configparser
import getopt
import glob
import os
import re
import shutil
import sys

from PIL import Image

import clip

__author__ = 'arnold'

config = configparser.ConfigParser()

directory = '/tmp'

rgba_re = re.compile(r'rgba\((\d+),\s*(\d+),\s*(\d+)\s*,(\d+\.\d+)\)')
color_set_re = re.compile(r'([^/]+)\.png')
file_opt_re = re.compile(r'[?!]$')
color_spec_re = re.compile(r'^([a-z]+)@([^:]+):(.*)')
assets_re = re.compile('/assets/[^/]+')
camel_caps_re = re.compile('_([a-z])')

aliases = {}
color_config = {}
name_fixes = {}
camel_caps = False


def configure_aliases():
    try:
        spec = config.items('aliases')
        for one, others in spec:
            names = others.split() + [one]
            for n in names:
                aliases[n] = names
    except configparser.NoSectionError:
        pass


def decode_color(color_nums, has_alpha=None):
    if not has_alpha:
        color_nums = color_nums[:3]
    elif len(color_nums) == 3:
        color_nums += (255,)
    return color_nums


def color_list(colors_config, has_alpha):
    lst = []
    for color_nums in colors_config:
        lst.append(decode_color(color_nums, has_alpha))
    return lst


def map_for(map_name, key_color, has_alpha):
    possible_keys = [key_color, ]
    try:
        possible_keys += aliases[key_color]
    except KeyError:
        pass

    first_key_error = None
    key_list = None
    for key in possible_keys:
        try:
            key_list = color_list(color_config[map_name][key], has_alpha)
            break
        except KeyError as e:
            if not first_key_error:
                first_key_error = e
    if not key_list:
        raise first_key_error

    num_colors = len(key_list)
    color_map = {}
    for color_name in color_config[map_name]:
        if color_name == key_color:
            continue
        colors_config = color_config[map_name][color_name]
        lst = color_list(colors_config, has_alpha)
        if len(lst) != num_colors:
            print(('Mismatch: %s: %s: expected %d colors, found %d' % (
                map_name, color_name, num_colors, len(lst))))
        else:
            m = {}
            for i in range(num_colors):
                m[key_list[i]] = lst[i]
            color_map[color_name] = m
    return color_map


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def decode_coloring(coloring):
    coloring_config = config.get('colorings', coloring)
    spec = coloring_config.split()
    if len(spec) == 3:
        spec.append('')
    return spec


def list_colors(color_name, file_name, exclude_colors):
    img = Image.open(file_name).convert('RGB')
    data = img.load()
    colors = set()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            r, g, b = data[x, y]
            colors.add((r, g, b))
    sys.stdout.write('%-13s' % (color_name + ':'))
    for c in sorted(colors, key=lambda x: sum(x), reverse=True):
        if c not in exclude_colors:
            # noinspection PyStringFormat
            sys.stdout.write(' %-13s' % ('(%d,%d,%d)' % c[:]))
    print('')


def to_camel_case(m):
    return m.group(1).upper()


def file_from_color(file_patterns, color_name):
    try:
        others = aliases[color_name]
    except KeyError:
        others = [color_name]

    m = color_spec_re.match(color_name)
    if m:
        color_name, pkg, key_file = m.groups()
        key_file = assets_re.sub('/assets/' + pkg, directory) + '/' + key_file
        return color_name, key_file
    for file_pat in file_patterns.split('|'):
        m = file_opt_re.search(file_pat)
        if m:
            file_opt = m.group(0)
            file_pat = file_opt_re.sub('', file_pat)
        else:
            file_opt = ''
        force = file_opt == '!'
        required = not force and file_opt != '?'
        for n in others:
            if camel_caps:
                n = camel_caps_re.sub(to_camel_case, n[0].capitalize() + n[1:])
            cpath = file_pat.replace('COLOR', n)
            if n in name_fixes:
                for pat in name_fixes[n]:
                    cpath = cpath.replace(pat[0], pat[1])
            if os.path.isfile(cpath) or force:
                return color_name, cpath

        # Handle the case where one color is the canonical one. For example, as of 1.9,
        # there is "sandstone.png" and "red_sandstone.png". The first is a yellow sandstone,
        # but it isn't called "yellow_sandstone.png" because when it was created, there was
        # only one color. So this code allows there to be a version of the file without the
        # "COLOR_" part of the file name, but only if it actually exists.
        cpath = file_pat.replace('COLOR_', '')
        if os.path.isfile(cpath):
            return color_name, cpath

        if required:
            raise Exception('No path found for %s in %s' % (file_pat, others))

    return color_name, ''


def list_image_colors(files):
    for f in files:
        src_img = Image.open(f)
        src_data = src_img.load()
        colors = set()
        for x in range(src_img.size[0]):
            for y in range(src_img.size[1]):
                colors.add(src_data[x, y])
        print('%s:' % f)
        for c in sorted(colors):
            print('  %s' % str(c))


def color_for(cell):
    try:
        style = str(cell.attrs['style'])
        rgba = rgba_re.search(style)
        return tuple(map(int, rgba.groups()[0:3])) + (int(round(float(rgba.group(4)) * 255)),)
    except KeyError:
        return clip.hex_to_rgba(cell.attrs['bgcolor'])[0:3]


def find_rows(img):
    data = img.load()
    bg_color = data[0, 0]
    rows = ()
    for y in range(img.size[1]):
        color = data[0, y]
        if color != bg_color:
            rows += (y + 1,)
    return rows


def find_cols(img):
    data = img.load()
    bg_color = data[0, 0]
    cols = ()
    for x in range(img.size[0]):
        color = data[x, 0]
        if color != bg_color:
            cols += (x + 1,)
    return cols


def build_name_fixes(fix_specs):
    if len(fix_specs) == 0:
        return None
    fixes = []
    for f in fix_specs:
        rhs, lhs = f.split('=')
        fixes.append([rhs, lhs])
    return fixes


def parse_colors():
    color_dir = clip.directory('config', 'colorize')
    for color_file in glob.glob('%s/*.png' % color_dir):
        img = Image.open(color_file)
        rows = find_rows(img)
        with open(color_file.replace('.png', '.txt')) as fp:
            name_lines = fp.read()
        names = name_lines.split('\n')[:-1]
        if len(names) != len(rows):
            raise Exception('%s: %d Names found for %d rows' % (color_file, len(names), len(rows)))
        cols = find_cols(img)
        data = img.load()

        which = color_set_re.search(color_file).group(1)
        i = 0
        color_set = {}
        for y in rows:
            colors = ()
            for x in cols:
                colors += (data[x, y],)
            name = names[i]
            name_split = name.split()
            if len(name_split) > 1:
                name = name_split[0]
                name_fixes[name] = build_name_fixes(name_split[1:])
            color_set[name] = colors
            i += 1
        color_config[which] = color_set
    return


def main(argv=None):
    global camel_caps

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'vhl:x:d',
                                       ['help', 'list', 'exclude', 'dump'])
        except getopt.error as msg:
            raise Usage(msg)
            # more code, unchanged
        if len(args) != 1:
            raise Usage('must specify one dir to process')
        global directory
        directory = args[0]
        os.chdir(directory)
    except Usage as err:
        print(err.msg, file=sys.stderr)
        print('for help use --help', file=sys.stderr)
        return 2

    parse_colors()
    config.read(['colorize.cfg', clip.directory('config', 'colorize.cfg')])
    try:
        camel_caps = config.getboolean('settings', 'camel_caps')
    except configparser.NoSectionError:
        pass

    exclude_colors = set()
    verbose = False
    # process options
    for o, a in opts:
        if o in ('-h', '--help'):
            print(__doc__)
            return 0
        if o in ('-d', '--dump'):
            list_image_colors(args)
            return 0
        elif o in ('-x', '--exclude'):
            color = decode_color(a, False)
            exclude_colors.add(color)
        if o in ('-v', '--verbose'):
            verbose = True

    configure_aliases()
    try:
        colorings = config.items('colorings')
    except configparser.NoSectionError:
        return 0

    warnf = open('README', 'w+')
    warnf.write('WARNING: The following files are generated by colorize.py:\n\n')
    for coloring, coloring_config in colorings:
        map_name, key_color, file_pat, ignore_spec = decode_coloring(coloring)
        ignores = tuple('' if x == "''" else x for x in ignore_spec.split(',')) if ignore_spec else ()
        # The key file is always required, so remove any options
        key_color, key_file = file_from_color(file_opt_re.sub('', file_pat), key_color)
        if verbose:
            print('%s: reading %s' % (coloring, key_file))
        src_img = Image.open(key_file)
        if src_img.mode == 'P':
            src_img = src_img.convert('RGB')
        src_data = src_img.load()
        num_channels = len(src_data[0, 0])
        has_alpha = num_channels > 3

        color_maps = map_for(map_name, key_color, has_alpha)
        for color_name, color_map in color_maps.items():
            if color_name in ignores:
                continue
            _, dst_file = file_from_color(file_pat, color_name)
            if dst_file == '':
                continue
            if verbose:
                print(('    %s' % dst_file))
            mode = 'RGB'
            if has_alpha:
                mode = 'RGBA'
            dst_img = Image.new(mode, src_img.size, color=(0, 0, 0, 0))
            dst_data = dst_img.load()
            for x in range(src_img.size[0]):
                for y in range(src_img.size[1]):
                    data = src_data[x, y][:num_channels]
                    try:
                        data = color_map[data]
                    except KeyError:
                        pass
                    dst_data[x, y] = data
            dst_img.save(dst_file, 'png', optimize=True)
            warnf.write('%s\n' % dst_file)
    warnf.write('\n')
    warnf.write('(The files are in git to help the script know which files should exist)\n')
    warnf.close()

    try:
        tweaks = config.items('tweaks')
        for _, tweak in tweaks:
            params = tweak.split()
            action = params[0]
            path = params[1]
            for target in params[2:]:
                shutil.copy2(path, target)
            if action == 'move':
                os.remove(path)
    except configparser.NoSectionError:
        pass


if __name__ == '__main__':
    sys.exit(main())
