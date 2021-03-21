import configparser
import glob
import os
import re

from PIL import Image

import clip

config = configparser.ConfigParser()
config.read(clip.directory('config', 'masked.cfg'))

os.chdir(clip.directory('textures'))
os.chdir('block')

for rpl, values in config.items('mappings'):
    pat, base, exclude = values.split()
    exclude = exclude[1:] if exclude[0] == '!' else exclude
    msk_img = Image.open(base + '.png').convert('RGBA')
    msk_dat = msk_img.getdata()
    rpl_img = Image.open(rpl + '.png').convert('RGBA')
    rpl_dat = rpl_img.getdata()
    assert (msk_img.size == rpl_img.size)
    for f in glob.glob(pat + '.png'):
        if re.search(exclude, f):
            continue
        src_img = Image.open(f).convert('RGBA')
        src_dat = src_img.getdata()
        out_dat = []
        assert (src_img.size == rpl_img.size)
        for p in range(0, len(src_dat)):
                src_pix = src_dat[p]
                msk_pix = msk_dat[p]
                rpl_pix = rpl_dat[p]
                out_dat.append(src_pix if src_pix != msk_pix else rpl_pix)
        out_img = Image.new('RGBA', src_img.size)
        out_img.putdata(out_dat)
        out_img.save('%s_%s' % (rpl, f), optimize=True)
