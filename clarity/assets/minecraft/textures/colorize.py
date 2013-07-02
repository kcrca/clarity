import ConfigParser
import re
import Image

__author__ = 'arnold'

config = ConfigParser.SafeConfigParser()
config.read('colorize.cfg')

color_pat = re.compile(r'\((\d+),(\d+),(\d+)\)')

colorings = config.items('colorings')
maps = {}


def color_list(color_name, colors_config):
    l = []
    colors = colors_config.split()
    for color in colors:
        m = color_pat.match(color)
        if not m:
            print('Bad color: %s: %s: %s' % (map_name, color_name, color))
        else:
            r, g, b = map(int, m.groups())
            l.append((r, g, b))
    return l


def map_for(map_name, key_color):
    key_list = color_list(key_color, config.get(map_name, key_color))
    num_colors = len(key_list)
    color_map = {}
    for color_name, colors_config in config.items(map_name):
        if color_name == key_color:
            continue
        l = color_list(color_name, colors_config)
        if len(l) != num_colors:
            print("Mismatch: %s: %s: expected %d colors, found %d" % (
                map_name, color_name, num_colors, len(l)))
        else:
            m = {}
            for i in xrange(num_colors):
                m[key_list[i]] = l[i]
            color_map[color_name] = m
    return color_map


for coloring, coloring_config in colorings:
    map_name, key_color, file_pat = coloring_config.split()
    color_maps = map_for(map_name, key_color)
    key_file = file_pat.replace('COLOR', key_color)
    src_img = Image.open(key_file)
    src_data = src_img.load()
    dst_img = Image.new('RGB', src_img.size, color=None)
    dst_data = dst_img.load()
    color_maps = map_for(map_name, key_color)
    for color_name, color_map in color_maps.iteritems():
        for x in xrange(src_img.size[0]):
            for y in xrange(src_img.size[1]):
                r, g, b, a = src_data[x, y]
                try:
                    r, g, b = color_map[(r, g, b)]
                except KeyError:
                    pass
                dst_data[x, y] = r, g, b
        dst_img.save(file_pat.replace('COLOR', color_name), "png")
