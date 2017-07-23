import os


def directory(name, *args):
    """
    Returns the directory with the specified name, as an absolute path.
    :param name: The name of the directory. One of "textures" or "models".
    :args Elements that will be appended to the named directory.
    :return: The full path of the named directory.
    """
    top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path = {
        "textures": "core/assets/minecraft/textures",
        "models": "core/assets/minecraft/models",
    }[name]
    path = os.path.join(top, path)
    for arg in args:
        for part in arg.split('/'):
           path = os.path.join(path, part)
    return path


def pretty(value):
    return "{:,}".format(value)


def hex_to_rgba(desc, alpha=255):
    return tuple(int(desc[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)
