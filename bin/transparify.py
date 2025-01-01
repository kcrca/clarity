#!/usr/bin/env python3

import os
import sys

from PIL import Image

for src_file in sys.argv[1:]:
    src_img = Image.open(src_file)
    src_data = src_img.convert('RGBA').load()

    dst_img = Image.new('RGBA', src_img.size, color=(0, 0, 0, 0))
    dst_data = dst_img.load()

    for x in range(src_img.size[0]):
        for y in range(src_img.size[1]):
            data = src_data[x, y]
            if data[3] == 0:
                level = 0
            else:
                level = data[0]
                if level < 10:
                    level = 0
            if data[3] not in [0, 255]:
                print(data)
            dst_data[x, y] = (255, 255, 255, level)

    os.rename(src_file, src_file.replace('.png', '_orig.png'))
    dst_img.save(src_file, 'png', optimize=True)
