#!/usr/bin/env python

import json
import Image

overrides = []

clock_img = Image.open('textures/items/clock.png')
clock_img.load()
size = clock_img.size[0]
ticks = clock_img.size[1] / size
tick_time = 1.0 / ticks
print '%d ticks' % ticks
for i in range(0, ticks):
    name = 'clock_%04d' % i
    texture = 'items/%s' % name
    png_path = texture + '.png'
    model = 'item/%s' % name
    json_path = 'item/%s.json' % name
    overrides.append({"predicate": {"time": i * tick_time}, "model": model})
    tick_img = clock_img.crop((0, i * size, size, (i + 1) * size))
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
            "layer0": "items/clock_0000"
        },
        "overrides": overrides
    }, f, indent=4, sort_keys=True)
