import os
import shutil
import math

from PIL import Image


class Square:
    next_direction = 1

    def __init__(self, pos, color, radius, size, frames):
        (self.center_x, self.center_y) = pos
        self.color = color
        self.radius = radius / 2
        self.size = size
        self.direction = Square.next_direction
        self.frames = frames
        Square.next_direction *= -1

    def alpha_adjust(self, frame_num):
        adjust = frame_num % self.frames
        if adjust >= self.frames / 2:
            adjust = abs(self.frames - adjust)
        if self.direction < 0:
            adjust = self.frames / 2 - adjust
        adjust += 2
        return adjust


def directory(name, *args):
    """
    Returns the directory with the specified name, as an absolute path.
    :param name: The name of the directory. One of "textures" or "models".
    :args Elements that will be appended to the named directory.
    :return: The full path of the named directory.
    """
    top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path = {
        'bin': 'bin',
        'config': 'bin',
        'top': '',
        'textures': 'core/assets/minecraft/textures',
        'models': "core/assets/minecraft/models",
        'minecraft': "core/assets/minecraft",
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
    if desc[0] == '#':
        desc = desc[1:]
    if len(desc) % 4 == 0:
        return tuple(int(desc[i:i + 2], 16) for i in (0, 2, 4, 6))
    result = tuple(int(desc[i:i + 2], 16) for i in (0, 2, 4))
    if alpha < 0:
        return result
    return result + (alpha,)


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


# This composites an image onto another merging the alpha properly. This should be part of PIL, but I can't find it.
# (This differs from Image.alpha_composite by working on a specific subimage.
# From http://stackoverflow.com/questions/3374878/with-the-python-imaging
# -library-pil-how-does-one-compose-an-image-with-an-alp
def alpha_composite(output, image, pos, rotation=0):
    if rotation:
        size = image.size
        image = image.rotate(rotation, expand=1).resize(size, Image.ANTIALIAS)
    r, g, b, a = image.split()
    rgb = Image.merge("RGB", (r, g, b))
    mask = Image.merge("L", (a,))
    output.paste(rgb, pos, mask)
