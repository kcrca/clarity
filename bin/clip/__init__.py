import os


def directory(name):
    """
    Returns the directory with the specified name, as an absolute path.
    :param name: The name of the directory. One of "textures" or "models".
    :return: The full path of the named directory.
    """
    top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    path = {
        "textures": "core/assets/minecraft/textures",
        "models": "core/assets/minecraft/models",
    }[name]
    return os.path.join(top, path)


def pretty(value):
    return "{:,}".format(value)
