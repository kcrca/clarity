#!/usr/bin/env python

# This program can be run on any set of png files. It will attempt to save each named file, checking to see if it
# saves space. If it does not, the original will be kept. It also makes sure that the new file is pixel-for-pixel
# identical to the original file.
#
# This can be left in the tree because it does nothing if no files are named.

__author__ = 'arnold'

import os
import sys
from PIL import Image, ImageChops
from clip import pretty

# If True, a file has alpha data that's all 255 will drop that alpha channel.
# If False, unused alpha channels will be retained.
remove_unused_alpha = False

saved_overall = 0
for f in sys.argv[1:]:
    size1 = os.stat(f).st_size
    with open(f, 'rb') as content:
        orig_bytes = content.read()
    raw1 = Image.open(f)
    img1 = raw1.convert("RGBA")
    alpha = img1.getdata(3)
    if remove_unused_alpha and (alpha) == 255 * img1.size[0] * img1.size[1]:
        img1 = raw1.convert("RGB")
    orig_data = img1.getdata()
    new_data = []
    for data in orig_data:
        if len(data) == 4 and data[3] == 0:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(data)
    img1.putdata(new_data)
    img1.save(f)
    size2 = os.stat(f).st_size
    raw2 = Image.open(f)
    img2 = raw2.convert(img1.mode)
    same = len(filter(lambda x: len(x) != 4 or x[3] != 0, ImageChops.difference(img1, img2).getdata())) == 0
    saved = size1 - size2
    note = ''
    if saved < 0:
        grew = -saved
        with open(f, 'wb') as content:
            content.write(orig_bytes)
        size2 = os.stat(f).st_size
        saved = size1 - size2
        assert saved == 0, "%s: not restored, saved: %d" % (f, saved)
        note = ' (grew %s!)' % pretty(grew)
    saved_overall += saved
    percent = int(round(100.0 * size2 / size1))
    print "%s: %d%%, %s [%s] (%s -> %s)%s" % (
        f, percent, pretty(saved), pretty(saved_overall), raw1.mode, raw2.mode, note)
    if not same:
        print "CHANGED!"
        sys.exit(1)
    if percent > 100:
        print "GREW!"
        sys.exit(1)
