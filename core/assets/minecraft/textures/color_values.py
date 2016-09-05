#!/usr/bin/env python

import re
import subprocess
import sys
from collections import OrderedDict

__author__ = 'arnold'

color_re = re.compile(r'srgba?\(((\d+),(\d+),(\d+),?(\d+)?)\)')


def file_char(file_num):
    return chr(file_num + ord('a'))

def rgb_as_num(rgb_str):
    m = color_re.search(rgb_str)
    rstr, gstr, bstr, astr = m.groups()[2:6]
    if astr == '':
        astr = '0'
    r, g, b, a = map(int, (rstr, gstr, bstr, astr))
    return ((((r * 256 + g) * 256) + b) * 256) + a


def sort_rgb(v1, v2):
    return rgb_as_num(v1) < rgb_as_num(v2)



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
                rgba = m.group(1)
                if not m.group(5):
                    rgba += ',1'
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
        print '%-20s %s' % (rgba, filestr)
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
