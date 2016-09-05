#!/usr/bin/env python

import re
import subprocess
import sys
from collections import OrderedDict

__author__ = 'arnold'

color_re = re.compile(r'#([\dA-Za-z]{6,8})')


def file_char(file_num):
    return chr(file_num + ord('a'))


def to_rgba(m):
    rgba = m.group(1).lower()
    if len(rgba) == 6:
        return rgba +"ff"
    return rgba


def quad(rgba):
    r, g, b, a = tuple(map(ord, rgba.decode('hex')))
    return '(%d,%d,%d,%d)' % (r, g, b, a)


def analyze(color):
    pngs = [line[2:] for line in subprocess.check_output('find . -iname "*%s*.png"' % color, shell=True).splitlines()]
    if len(pngs) == 0:
        print "No matches for %s" % color
        return
    rgbas = OrderedDict()
    for i in range(0, len(pngs)):
        f = pngs[i]
        for line in subprocess.check_output('convert %s -unique-colors txt:-' % f, shell=True).splitlines():
            m = color_re.search(line)
            if m:
                rgba = to_rgba(m)
                try:
                    rgbas[rgba].append(i)
                except KeyError:
                    rgbas[rgba] = [i]
        if len(rgbas) == 0:
            print "No colors found in %s" % f
    for rgba in rgbas:
        filestr = ''
        indices = rgbas[rgba]
        for i in range(0, len(pngs)):
            filestr += file_char(i) if i in indices else ' '
        print '#%s %-20s %s' % (rgba, quad(rgba), filestr)
    print ''
    for i in range(0, len(pngs)):
        print '%c: %s' % (file_char(i), pngs[i])


def main(argv=None):
    if argv is None:
        argv = sys.argv
    for color in argv[1:]:
        analyze(color)


if __name__ == '__main__':
    sys.exit(main())
