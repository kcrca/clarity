#!/usr/bin/env python3
import configparser
import glob
import os
import re
import shutil
import sys

from PIL import Image

import clip

__author__ = 'arnold'

config = configparser.ConfigParser()
config.read(clip.directory('config', 'villagers.cfg'))

hair_re = re.compile(r'([^@]*)(?:@(\d+\.?\d*))?')
brows_re = re.compile(r'(\d+)@(\d+),(\d+)')
hair_color_re = re.compile(r'(\d+),(\d+)')
avatar_dir = clip.directory('minecraft', 'optifine', 'random', 'entity', 'villager', 'profession')
shutil.rmtree(avatar_dir, ignore_errors=True)
os.makedirs(avatar_dir)

for filename in glob.glob('%s/*' % avatar_dir):
    os.unlink(filename)

people_config = config.items('people')

style_imgs = {}
hair_imgs = {}
villager_imgs = {}
career_imgs = {}
skin_imgs = {}

os.chdir(clip.directory('textures', 'entity', 'villager'))

career_files = ()
for file in glob.glob('parts/*.png'):
    name = os.path.basename(file)
    if not name.startswith('skin') and not name.startswith('hair'):
        career_files += (file,)

careers = ()
for f in career_files:
    career = os.path.basename(f)[:-4]
    careers += (career,)
    career_imgs[career] = Image.open(f).convert("RGBA")

all_desc = config.get('people', 'all')
all_hairs = all_desc.split()

only_listed = set()
only_listed_desc = config.get('settings', 'only_listed')
if only_listed_desc:
    only_listed = set(only_listed_desc.split())

eyebrows = ()
eyebrows_desc = config.get('settings', 'eyebrows')
if eyebrows_desc:
    for brow_desc in eyebrows_desc.split():
        m = brows_re.match(brow_desc)
        brow_width, x, y = m.groups()
        eyebrows += (tuple((int(v) for v in m.groups()), ),)

no_eyebrows = set(config.get('settings', 'no_eyebrows').split())

hair_color_pos = []
hair_color_desc = config.get('settings', 'hair_color').split()
if hair_color_desc:
    for i in range(0, len(hair_color_desc)):
        m = hair_color_re.match(hair_color_desc[i])
        hair_color_pos.append(tuple(int(v) for v in m.groups()))

if (len(eyebrows) > 0) != (len(hair_color_pos) > 0):
    print("Must specify both eyebrows and hair_color pos, or neither.")
    sys.exit(1)

hair_styles = []
hair_style_desc = config.get('settings', 'styles').split()
if hair_style_desc:
    for i in range(0, len(hair_style_desc)):
        m = hair_re.match(hair_style_desc[i])
        hair_styles.append(m.groups())
    remaining = 100.0
    equal_chance = 0
    for style in hair_styles:
        cut, chance = style
        if chance is None:
            equal_chance += 1
        else:
            remaining -= float(chance)
    for i in range(0, len(hair_styles)):
        cut, chance = hair_styles[i]
        if chance is None:
            hair_styles[i] = (cut, (remaining / equal_chance))
        else:
            hair_styles[i] = (cut, float(chance))


def build_avatars(career):
    avatar_num = 1
    career_img = career_imgs[career]
    odds = {}
    genotypes = {}
    styles = {}
    same_hair = {}
    for skin, hair_descs in people_config:
        if skin == 'all':
            continue

        if skin in skin_imgs:
            skin_img = skin_imgs[skin]
        else:
            skin_path = 'parts/%s.png' % skin
            skin_img = skin_imgs[skin] = Image.open(skin_path).convert('RGBA')

        hairs = hair_descs.split()
        if skin not in only_listed:
            hairs += all_hairs
        for style_desc in hair_styles:
            for hair_desc in hairs:
                m = hair_re.match(hair_desc)
                hair, percent = m.groups()
                style, style_percent = style_desc
                if style == 'shaved':
                    hair_path = 'parts/hair_styles/hair_%s.png' % style
                else:
                    hair_path = 'parts/hair_styles/test_crap/hair_%s_%s.png' % (style, hair)

                if (hair, style) in hair_imgs:
                    hair_img = hair_imgs[(hair, style)]
                else:
                    hair_img = hair_imgs[(hair, style)] = Image.open(hair_path).convert('RGBA')
                if (hair, style) in same_hair:
                    same_hair[(hair, style)] += (avatar_num,)
                else:
                    same_hair[(hair, style)] = (avatar_num,)
                if style != 'shaved':
                    genotype = '%s_%s_%s' % (skin, hair, style)
                else:
                    genotype = '%s_%s' % (skin, style)
                genotypes[avatar_num] = genotype
                styles[avatar_num] = (style, style_percent)
                if percent:
                    if style != 'shaved':
                        odds[avatar_num] = (float(percent) / 100) * (style_percent / 100) * 100
                    else:
                        odds[avatar_num] = style_percent
                img = Image.alpha_composite(skin_img, career_img)

                # Special case for eyebrows
                if hair not in no_eyebrows and eyebrows:
                    hair_color = [0, 0, 0, 0]
                    for color_pos in hair_color_pos:
                        if hair_color[3] != 0:
                            continue
                        hair_color = hair_img.getpixel(color_pos)
                    # Alpha is zero, so no real hair color
                    if hair_color[3] != 0:
                        eyebrow_color = clip.darker(hair_color[0:3]) + (hair_color[3],)
                        for eyebrow in eyebrows:
                            length, x, y = eyebrow
                            for i in range(0, length):
                                # Need eyebrows only if the career image hasn't set the pixel
                                need_eyebrows = career_img.getpixel((x, y))[3] == 0
                                if need_eyebrows:
                                    img.putpixel((x + i, y), eyebrow_color)
                img = Image.alpha_composite(img, hair_img)

                avatar_path = '%s/%s%d.png' % (avatar_dir, career, avatar_num)
                img.save(avatar_path)
                avatar_num += 1
                if style == 'shaved':
                    break

    # adjust odds for the number of folks with the same hair.
    for (hair, style) in same_hair:
        same = same_hair[(hair, style)]
        if same[0] in odds:
            for i in same:
                odds[i] /= len(same)
    return avatar_num - 1, odds, genotypes, styles


for career in career_imgs:
    num_avatars, odds, genotypes, styles = build_avatars(career)

    prop_path = '%s/%s.properties' % (avatar_dir, career)
    props = open(prop_path, 'w')

    odds_specified = sum(odds[i] for i in odds)

    remaining = 100.0 - odds_specified
    assert remaining > 0
    default_odds = remaining / (num_avatars - len(odds))
    weights = ''
    t = 0.0
    style_percentages = []
    for i in range(1, num_avatars + 1):
        weight = odds[i] if i in odds else default_odds
        if len(weights) > 0:
            weights += ','
        t += weight
        # use max to make sure nothing has zero chance.
        weights += str(max(1, int(round(weight * 1000))))
        props.write('# %2d: %6.7f %s\n' % (i, weight, genotypes[i]))

    props.write('#     %6.3f\n' % t)
    props.write('professions.1=%s\n' % career)
    props.write('skins.1=1-%d\n' % num_avatars)
    props.write('weights.1=%s\n' % weights)
    props.close()
