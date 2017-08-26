#!/usr/bin/env python

import os
import shutil
import sys
import getopt
import ConfigParser
import re
from PIL import Image
from bs4 import BeautifulSoup
import clip

__author__ = 'arnold'

config = ConfigParser.SafeConfigParser()

directory = '/tmp'

color_re = re.compile(r'\(?\s*(\d+),\s*(\d+),\s*(\d+),?\s*(\d+)?\s*\)?')
rgba_re = re.compile(r'rgba\((\d+),\s*(\d+),\s*(\d+)\s*,(\d+\.\d+)\)')
file_opt_re = re.compile(r'\?$')
color_spec_re = re.compile(r'^([a-z]+)@([^:]+):(.*)')
assets_re = re.compile('/assets/[^/]+')
camel_caps_re = re.compile('_([a-z])')

aliases = {}
color_config = {}
camel_caps = False


def configure_aliases():
    try:
        spec = config.items('aliases')
        for one, others in spec:
            names = others.split() + [one]
            for n in names:
                aliases[n] = names
    except ConfigParser.NoSectionError:
        pass


def decode_color(color_nums, has_alpha=None):
    if not has_alpha:
        color_nums = color_nums[:3]
    elif len(color_nums) == 3:
        color_nums += (255,)
    return color_nums


def color_list(colors_config, has_alpha):
    l = []
    for color_nums in colors_config:
        l.append(decode_color(color_nums, has_alpha))
    return l


def map_for(map_name, key_color, has_alpha):
    key_list = color_list(color_config[map_name][key_color], has_alpha)
    num_colors = len(key_list)
    color_map = {}
    for color_name in color_config[map_name]:
        if color_name == key_color:
            continue
        colors_config = color_config[map_name][color_name]
        l = color_list(colors_config, has_alpha)
        if len(l) != num_colors:
            print('Mismatch: %s: %s: expected %d colors, found %d' % (
                map_name, color_name, num_colors, len(l)))
        else:
            m = {}
            for i in xrange(num_colors):
                m[key_list[i]] = l[i]
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
    for x in xrange(img.size[0]):
        for y in xrange(img.size[1]):
            r, g, b = data[x, y]
            colors.add((r, g, b))
    sys.stdout.write('%-13s' % (color_name + ':'))
    for c in sorted(colors, cmp=lambda x, y: sum(x) - sum(y), reverse=True):
        if not c in exclude_colors:
            # noinspection PyStringFormat
            sys.stdout.write(' %-13s' % ('(%d,%d,%d)' % c[:]))
    print ''

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
        orig_pat = file_pat
        file_pat = file_opt_re.sub('', file_pat)
        required = file_pat == orig_pat
        for n in others:
            if camel_caps:
                n = camel_caps_re.sub(to_camel_case, n[0].capitalize() + n[1:])
            cpath = file_pat.replace('COLOR', n)
            if os.path.isfile(cpath):
                return color_name, cpath

        # Handle the case where one color is the canonical one. For example, as of 1.9,
        # there is "sandstone.png" and "red_standstone.png". The first is a yellow sandstone,
        # but it isn't called "yellow_standstong.png" because when it was created, there was
        # only one color. So this code allows there to be a version of the file without the
        # "COLOR_" part of the file name, but only if it actually exists.
        cpath = file_pat.replace('COLOR_', '')
        if os.path.isfile(cpath):
            return color_name, cpath

        if required:
            raise Exception('No path found for %s in %s' % (file_pat, others))

        # there is "sandstone.png" and "red_standstone.png". The first is a yellow sandstone,
        # but it isn't called "yellow_standstong.png" because when it was created, there was
        # only one color. So this code allows there to be a version of the file without the
        # "COLOR_" part of the file name, but only if it actually exists.
        cpath = file_pat.replace('COLOR_', '')
        if os.path.isfile(cpath):
            return color_name, cpath

        if required:
            raise Exception('No path found for %s in %s' % (file_pat, others))

    return color_name, ''


def list_coloring(coloring, exclude_colors):
    map_name, key_color, file_pat = decode_coloring(coloring)
    # For listing, nothing is required, so remove the options
    file_pat = re.sub(file_opt_re, file_pat, '')
    key_file = file_from_color(re.sub(file_opt_re, file_pat, ''), key_color)
    print '[%s]' % coloring
    print ''
    list_colors(key_color, key_file, exclude_colors)
    file_re = re.compile(file_from_color(os.path.basename(file_pat), r'(.*)'))
    file_dir = os.path.dirname(file_pat)
    for f in sorted(os.listdir(file_dir)):
        m = file_re.match(f)
        if m:
            color_name = m.groups()[0]
            list_colors(color_name, '%s/%s' % (file_dir, f), exclude_colors)


def list_image_colors(files):
    for f in files:
        src_img = Image.open(f)
        src_data = src_img.load()
        colors = set()
        for x in xrange(src_img.size[0]):
            for y in xrange(src_img.size[1]):
                colors.add(src_data[x, y])
        print '%s:' % f
        for c in sorted(colors):
            print '  %s' % str(c)


def color_for(cell):
    try:
        style = str(cell.attrs['style'])
        rgba = rgba_re.search(style)
        return tuple(map(int, rgba.groups()[0:3])) + (int(round(float(rgba.group(4)) * 255)),)
    except KeyError:
        return clip.hex_to_rgba(cell.attrs['bgcolor'])[0:3]


def parse_colors():
    with open(clip.directory('config', 'colorize.html')) as fp:
        doc = BeautifulSoup(fp, 'html.parser')
        for table in doc.find_all('table'):
            section = {}
            which = str(table.caption.contents[0]).strip()
            for row in table.find_all('tr'):
                colors = ()
                try:
                    if row.attrs['class'][0] == u'Note':
                        continue
                except KeyError:
                    pass
                row_name = ''
                for cell in row.find_all('td'):
                    if row_name == '':
                        row_name = str(cell.contents[0]).strip()
                    else:
                        colors += (color_for(cell),)
                section[row_name] = colors
            color_config[which] = section


def main(argv=None):
    global camel_caps

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], 'hl:x:d',
                                       ['help', 'list', 'exclude', 'dump'])
        except getopt.error, msg:
            raise Usage(msg)
            # more code, unchanged
        if len(args) != 1:
            raise Usage('must specifiy one dir to process')
        global directory
        directory = args[0]
        os.chdir(directory)
    except Usage, err:
        print >> sys.stderr, err.msg
        print >> sys.stderr, 'for help use --help'
        return 2

    parse_colors()
    config.read(['colorize.cfg', clip.directory('config', 'colorize.cfg')])
    try:
        camel_caps = config.getboolean('settings', 'camel_caps')
    except ConfigParser.NoSectionError:
        pass

    list_colorings = []
    exclude_colors = set()
    # process options
    for o, a in opts:
        if o in ('-h', '--help'):
            print __doc__
            return 0
        if o in ('-d', '--dump'):
            list_image_colors(args)
            return 0
        if o in ('-l', '--list'):
            list_colorings.append(a)
        elif o in ('-x', '--exclude'):
            color = decode_color(a, False)
            exclude_colors.add(color)

    if len(list_colorings):
        for coloring in list_colorings:
            list_coloring(coloring, exclude_colors)
        return 0

    configure_aliases()
    try:
        colorings = config.items('colorings')
    except ConfigParser.NoSectionError:
        return 0

    warnf = open('README', 'w+')
    warnf.write('WARNING: The following files are generated by colorize.py:\n\n')
    for coloring, coloring_config in colorings:
        map_name, key_color, file_pat, ignore_spec = decode_coloring(coloring)
        ignores = ignore_spec.split(',') if ignore_spec else ()
        # The key file is always required, so remove any options
        key_color, key_file = file_from_color(file_opt_re.sub('', file_pat), key_color)
        print '%s: reading %s' % (coloring, key_file)
        src_img = Image.open(key_file)
        if src_img.mode == 'P':
            src_img = src_img.convert('RGB')
        src_data = src_img.load()
        num_channels = len(src_data[0, 0])
        has_alpha = num_channels > 3

        color_maps = map_for(map_name, key_color, has_alpha)
        for color_name, color_map in color_maps.iteritems():
            if color_name in ignores:
                continue
            _, dst_file = file_from_color(file_pat, color_name)
            if dst_file == '':
                continue
            print ('    %s' % dst_file)
            mode = 'RGB'
            if has_alpha:
                mode = 'RGBA'
            dst_img = Image.new(mode, src_img.size, color=None)
            dst_data = dst_img.load()
            for x in xrange(src_img.size[0]):
                for y in xrange(src_img.size[1]):
                    data = src_data[x, y][:num_channels]
                    try:
                        data = color_map[data]
                    except KeyError:
                        pass
                    dst_data[x, y] = data
            dst_img.save(dst_file, 'png')
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
    except ConfigParser.NoSectionError:
        pass


if __name__ == '__main__':
    sys.exit(main())
