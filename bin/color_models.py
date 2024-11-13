#!/usr/bin/env python3

__author__ = 'arnold'

import glob

import clip

for f in glob.glob(f'{clip.directory("models")}*/cyan_*.json') + glob.glob(
        f'{clip.directory("minecraft")}/items/cyan_*.json'):
    with open(f) as src_file:
        src = src_file.read()
        for c in clip.colors:
            if c == 'cyan':
                pass
            path = f.replace('cyan', c)
            contents = src.replace('cyan', c)
            with  open(path, 'w') as dst_file:
                dst_file.write(contents)
