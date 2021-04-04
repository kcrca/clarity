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

msk_img = Image.open('stone.png').convert('RGBA')
msk_dat = msk_img.getdata()
rpl_img = Image.open('deepslate.png').convert('RGBA')
rpl_dat = rpl_img.getdata()
top_rpl_img = Image.open('deepslate_top.png').convert('RGBA')
top_rpl_dat = top_rpl_img.getdata()
for f in glob.glob('*_ore.png'):
    if re.search('deepslate|nether', f) is not None:
        continue
    src_img = Image.open(f).convert('RGBA')
    src_dat = src_img.getdata()
    out_dat = []
    top_dat = []
    for p in range(0, len(src_dat)):
        src_pix = src_dat[p]
        msk_pix = msk_dat[p]
        out_dat.append(src_pix if src_pix != msk_pix else rpl_dat[p])
        top_dat.append(src_pix if src_pix != msk_pix else top_rpl_dat[p])
    ore_name = f[:-4]

    out_img = Image.new('RGBA', src_img.size)
    out_img.putdata(out_dat)
    out_img.save('deepslate_%s.png' % ore_name, optimize=True)

    top_img = Image.new('RGBA', src_img.size)
    top_img.putdata(top_dat)
    top_img.save('deepslate_%s_top.png' % ore_name, optimize=True)
