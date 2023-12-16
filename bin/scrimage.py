#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from PIL import Image


def percent_of(before, after):
    if after == 0:
        return 0
    return int(100 * (1 - float(after) / before))


class Scrimage:
    def __init__(self, verbose=1):
        self.verbose = verbose

    def scrimage(self, *paths):
        totals = [0, 0]
        if len(paths) == 0:
            return []
        if len(paths) > 1:
            for p in paths:
                nums = self.scrimage(p)
                totals[0] += nums[0]
                totals[1] += nums[1]
            return totals
        path = Path(paths[0])
        if path.is_dir() and not path.is_symlink():
            return self.scrimage(*path.glob('*'))
        try:
            img = Image.open(path)
            saved = percent = before = 0
            changed = False
            if img.info:
                changed = True
                img.info = {}
            if img.mode.endswith('A'):
                _, _, _, a = img.split()
                if not any(lambda x: x != 255 for x in list(a.getdata())):
                    img = img.convert(img.mode[:-1])
                    changed = True
            if changed:
                if self.verbose:
                    before = os.stat(path).st_size
                img.save(path)
                if self.verbose:
                    after = os.stat(path).st_size
                    saved = before - after
                    percent = percent_of(before, after)
                    totals[0] += before
                    totals[1] += after
            if self.verbose > 1 or (self.verbose == 1 and before != after):
                print(f'{path}: {saved:,}b / {percent}%')
        except:
            pass
        return totals


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='scrunch images to smaller sizes losslessly')
    parser.add_argument('-verbose', '-v', action='count', default=0)
    parser.add_argument('path', action='append', type=Path)
    options = parser.parse_args()
    scrimage = Scrimage(verbose=options.verbose)
    totals = scrimage.scrimage(*options.path)
    if scrimage.verbose and totals:
        print(f'Total: {totals[0]:,}b / {percent_of(*totals)}%')
