#!/usr/bin/env python
import ConfigParser
import glob
import os
import re

import errno
from PIL import Image

hair_re = re.compile(r'([^@]*)(?:@(\d+\.?\d*))?')
avatar_dir = '../../../mcpatcher/mob/villager'
for filename in glob.glob('%s/*' % avatar_dir):
    os.unlink(filename)

config = ConfigParser.SafeConfigParser()
config.read('villagers.cfg')

people_config = config.items('people')
canonical_config = config.items('canonical')

hair_imgs = {}
villager_imgs = {}
career_imgs = {}
skin_imgs = {}

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

canonical = {}
for career, desc in canonical_config:
    canonical[career] = desc.split()

all_desc = config.get('people', 'all')
all_hairs = all_desc.split()


def build_avatars(career):
    avatar_num = 1
    career_img = career_imgs[career]
    odds = {}
    genotypes = {}
    same_hair = {}
    for skin, hair_descs in people_config:
        if skin == 'all':
            continue

        if skin in skin_imgs:
            skin_img = skin_imgs[skin]
        else:
            skin_path = 'parts/%s.png' % skin
            skin_img = skin_imgs[skin] = Image.open(skin_path).convert('RGBA')

        for hair_desc in hair_descs.split() + all_hairs:
            m = hair_re.match(hair_desc)
            hair, percent = m.groups()
            hair_path = 'parts/hair_%s.png' % hair
            if hair in hair_imgs:
                hair_img = hair_imgs[hair]
            else:
                hair_img = hair_imgs[hair] = Image.open(hair_path).convert('RGBA')
            if hair in same_hair:
                same_hair[hair] += (avatar_num,)
            else:
                same_hair[hair] = (avatar_num,)
            genotype = '%s_%s' % (skin, hair)
            genotypes[avatar_num] = genotype
            if percent:
                odds[avatar_num] = float(percent)
            img = Image.alpha_composite(skin_img, career_img)
            img = Image.alpha_composite(img, hair_img)
            avatar_num_str = str(avatar_num)
            avatar_path = '%s/%s%s.png' % (avatar_dir, career, avatar_num_str)
            img.save(avatar_path)
            avatar_num += 1
            if career == 'butcher':
                print avatar_num
            if canonical[career] == [skin, hair]:
                img.save('%s.png' % career)
                print 'Canonical %s: %s' % (career, genotype)

    # adjust odds for the number of folks with the same hair.
    for hair in same_hair:
        same = same_hair[hair]
        if same[0] in odds:
            for i in same:
                odds[i] /= len(same)
    return avatar_num - 1, odds, genotypes


for career in career_imgs:
    num_avatars, odds, genotypes = build_avatars(career)

    prop_path = '%s/%s.properties' % (avatar_dir, career)
    props = open(prop_path, 'w')

    odds_specified = sum(odds[i] for i in odds)

    remaining = 100.0 - odds_specified
    assert remaining > 0
    default_odds = remaining / (num_avatars - len(odds))
    weights = ''
    t = 0.0
    for i in range(1, num_avatars + 1):
        weight = odds[i] if i in odds else default_odds
        if len(weights) > 0:
            weights += ','
        t += weight
        weights += str(int(round(weight * 1000)))
        props.write('# %2d: %6.3f %s\n' % (i, weight, genotypes[i]))

    props.write('#     %6.3f\n' % t)
    props.write('skins.1=1-%d\n' % num_avatars)
    props.write('weights.1=%s\n' % weights)
    props.close()
