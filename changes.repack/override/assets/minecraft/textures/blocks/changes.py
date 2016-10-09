#!/usr/bin/env python

import os
import getopt
import json
import collections
import Image

__author__ = 'arnold'

weeks_in_year = 52

timings = collections.OrderedDict()
timings['autumn'] = 2
timings['winter'] = 8
timings['spring'] = 2

day = 24000

debug_timing = False
if debug_timing:
    weeks_in_year = 8
    timings['winter'] = 2
    day = 2

week = day * 7
transition = week / 2
timings['summer'] = weeks_in_year - sum(timings[x] for x in timings)
year = weeks_in_year * week

if debug_timing:
    transition = 70

frames =[]
anim_json = {
    "animation": {
        "frametime": transition,
        "frames": frames,
    }
}

index = 0
for season in timings:
    duration = timings[season]
    stay_time = duration * week - transition
    if debug_timing:
        stay_time = week
    frame_json = {'index': index, 'time': stay_time}
    frames.append(frame_json)
    frames.append(index)
    index += 1

transparent=(0,0,0,0)
for tree in ('oak','birch','jungle', 'big_oak', 'acacia'):
    leaves_img = None
    branches_img = None
    h = 0
    index = 0
    for season in timings:
        season_img = Image.open('%s/leaves_%s.png' % (season, tree))
        if not leaves_img:
            w, h = season_img.size
            leaves_img = Image.new(season_img.mode, (w, 4 * h), transparent)
            branches_img = Image.new(season_img.mode, (w, 4 * h), transparent)
        frame_pos = h * index
        if season == 'winter':
            branches_img.paste(season_img, (0, frame_pos))
        else:
            leaves_img.paste(season_img, (0, frame_pos))
        index += 1
    anim_json['animation']['interpolate'] = True
    with open('leaves_%s.png.mcmeta' % tree, 'w') as f:
        json.dump(anim_json, f, indent=2)
    anim_json['animation']['interpolate'] = False
    with open('branches_%s.png.mcmeta' % tree, 'w') as f:
        json.dump(anim_json, f, indent=2)
    leaves_img.save('leaves_%s.png' % tree)
    branches_img.save('branches_%s.png' % tree)
