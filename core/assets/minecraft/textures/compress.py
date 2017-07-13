#!/usr/bin/env python
import locale
import os
import sys
from PIL import Image, ImageChops


def pretty(value):
    return "{:,}".format(value)

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
    img1.save(f)
    size2 = os.stat(f).st_size
    raw2 = Image.open(f)
    img2 = raw2.convert(img1.mode)
    zero_pixel = (0, 0, 0, 0) if img1.mode == "RGBA" else (0, 0, 0)
    same = len(filter(lambda x: x != zero_pixel, ImageChops.difference(img1, img2).getdata())) == 0
    saved = size1 - size2
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
    print "%s: %d%%, %s [%s] (%s -> %s)%s" % (f, percent, pretty(saved), pretty(saved_overall), raw1.mode, raw2.mode, note)
    if not same:
        print "CHANGED!"
        sys.exit(1)
    if percent > 100:
        print "GREW!"
        sys.exit(1)
