#!/usr/bin/env python

from PIL import Image

__author__ = 'arnold'

particles = {
    "angry": ((1, 5),),
    "bubble": ((0, 2),),
    "bubble_pop": (2, (0, 16), 5),
    "critical_hit": ((0, 4),),
    "damage": ((3, 4),),
    "drip_fall": ((1, 7),),
    "drip_hang": ((0, 7),),
    "drip_land": ((2, 7),),
    "effect": ((0, 8), 8),
    "enchanted_hit": ((2, 4),),
    "flame": ((0, 3),),
    "flash": (4, (4, 2)),
    "generic": ((0, 0), 8),
    "glint": ((2, 5),),
    "glitter": ((0, 11), 8),
    "heart": ((0, 5),),
    "lava": ((1, 3),),
    "nautilus": ((0, 13),),
    "note": ((0, 4),),
    "sga": (lambda x: "_%c" % chr(x + ord('a')), (1, 14), 15, (0, 15), 11),
    "spark": ((0, 10), 8),
    "spell": ((0, 9), 8),
    "splash": ((3, 1), 4),
}

master = Image.open("particles.png").convert('RGBA')
base_size = master.size[0] * 8 / 256

for particle in particles:
    spec = particles[particle]
    num_str = lambda x: "_%d" % x
    if callable(spec[0]):
        num_str = spec[0]
        spec = spec[1:]
    size = base_size
    if isinstance(spec[0], int):
        size = spec[0] * base_size
        spec = spec[1:]
    num = 0
    while len(spec) > 0:
        first = spec[0]
        spec = spec[1:]
        count = 1
        if len(spec) > 0:
            count = spec[0]
            spec = spec[1:]
        cur = tuple(n * base_size for n in first)
        for i in range(0, count):
            p = master.crop((cur[0], cur[1], cur[0] + size, cur[1] + size))
            name = particle
            if count > 1:
                name += num_str(num)
            p.save(name + ".png")
            num += 1
            cur = (cur[0] + size, cur[1])
