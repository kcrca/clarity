#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image


def percent_of(before, after):
    if after == 0:
        return 0
    return int(100 * (1 - float(after) / before))


class Scrimage:
    no_alpha = {255}

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
        temp = None
        # noinspection PyBroadException
        try:
            img = Image.open(path)
            saved = percent = 0
            changed = False
            if 'XML:com.adobe.xmp' in img.info:
                del img.info['XML:com.adobe.xmp']
                changed = True
            if img.mode.endswith('A'):
                alphas = set(img.getdata(len(img.getbands()) - 1))
                if alphas == Scrimage.no_alpha:
                    img = img.convert(img.mode[:-1])
                    changed = True
            if changed:
                before = os.stat(path).st_size
                dirname, basename = os.path.split(path)
                ts = tempfile.NamedTemporaryFile(prefix=path.name[:-len(path.suffix) - 1], dir=dirname,
                                                 suffix=path.suffix, delete=False)
                temp = Path(ts.name)
                img.save(temp)
                after = os.stat(temp).st_size
                if after >= before:
                    temp.unlink()
                else:
                    temp.rename(path)
                    saved = before - after
                    percent = percent_of(before, after)
                    totals[0] += before
                    totals[1] += after
            if self.verbose > 1 or (self.verbose == 1 and saved > 0):
                print(f'{path}: {saved:,}b / {percent}%')
        except FileNotFoundError as e:
            raise e
        except:
            # If the temp file was created, but an error happened in the middle, remove it
            if temp:
                temp.unlink()
            pass
        return totals


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='scrunch images to smaller sizes losslessly')
        parser.add_argument('-verbose', '-v', action='count', default=0)
        parser.add_argument('path', action='append', type=Path)
        options = parser.parse_args()
        scrimage = Scrimage(verbose=options.verbose)
        totals = scrimage.scrimage(*options.path)
        if scrimage.verbose and totals:
            print(f'Total: {totals[0]:,}b / {percent_of(*totals)}%')
