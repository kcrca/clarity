#!/usr/bin/env python3
"""
This file is partially written, but valuable maybe in the future. With 26.1-snapshot-7, minecraft introduced a way to
specify transparency in block textures, and distributed model files for glass and redstone that used this. But these all
seem to work just fine without those keywords, so I'm stopping development on this. The sys.exit() at the front means
that it will do nothing unless given an argument, which means it has no effect unless run manually (though this
argument is currently ignored).

The idea was to go through all the block model textures looking for transparency and marking those textures has having
transparency. This does not work, but it's close.
"""
import sys
import glob
import json
import clip

from PIL import Image

if len(sys.argv) == 1:
    sys.exit(0)

known = {}
images = clip.directory('textures')

for f in glob.glob(clip.directory('models', 'block/**/.json')):
    fp = open(f)
    js = json.load(fp)
    if 'textures' in js:
        changed = False
        textures = js['textures']
        for k, v in textures.items():
            if isinstance(v, str):
                if v in known:
                    translucent = known[v]
                else:
                    img = Image.open(f'{images}/{v.replace("minecraft:", "")}.png')
                    known[v] = translucent = clip.has_transparency(img)
                if translucent:
                    textures[k] = {'force_transparent': True, 'sprite': v}
                    changed = True
        if changed:
            json.dump(js, open(f, 'w'), indent=4)
