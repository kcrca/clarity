import os
import shutil

import math


class Square:
    next_direction = 1

    def __init__(self, pos, color, radius, size):
        (self.center_x, self.center_y) = pos
        self.color = color
        self.radius = radius / 2
        self.size = size
        self.direction = Square.next_direction
        Square.next_direction *= -1


def directory(name, *args):
    """
    Returns the directory with the specified name, as an absolute path.
    :param name: The name of the directory. One of "textures" or "models".
    :args Elements that will be appended to the named directory.
    :return: The full path of the named directory.
    """
    top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path = {
        'top': '',
        'textures': 'core/assets/minecraft/textures',
        'models': "core/assets/minecraft/models",
        'site': 'site',
    }[name]
    path = os.path.join(top, path)
    for arg in args:
        for part in arg.split('/'):
            path = os.path.join(path, part)
    return path


def clear_out_tree(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)
    return dir_name


def pretty(value):
    return "{:,}".format(value)


def hex_to_rgba(desc, alpha=255):
    return tuple(int(desc[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def num_digits(value):
    return int(math.ceil(math.log(value, 10)))


def iround(f):
    return int(round(f))


def adjust(color, steps, factor):
    for i in range(0, steps):
        color = tuple(c * factor for c in color[:3])
    return tuple(iround(c) for c in color)


def darker(c, steps):
    return adjust(c, steps, 0.9)


def lighter(c, steps):
    return adjust(c, steps, 1.15)
