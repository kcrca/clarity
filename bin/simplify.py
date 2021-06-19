import copy
import glob
import json
import os
import sys

import clip

# This script is a partial attempt at doing two things: First, it finds files that have rotational variants for
# aesthetic reasons. This screws up all sorts of things for Clarity, especially with connected textures. This job
# it does well.
#
# It also tries to build a simplified variant. That it doesn't do that so well, because some of them needs some special
# handling. So we disable it for automatic runs, but running it when a new texture pack arrives will tell us which
# blockstate files to look at and fix manually.
if len(sys.argv) == 1:
    sys.exit(0)

allow = tuple('%s.json' % x for x in ('sea_pickle', 'turtle_egg', 'lily_pad'))
new_states = {}
for file in glob.glob('%s/*.json' % clip.directory('defaults', 'blockstates')):
    if os.path.basename(file) in allow:
        continue
    old_bs = json.load(open(file))
    if 'variants' not in old_bs:
        continue
    new_bs = copy.deepcopy(old_bs)
    simplified = []
    orig_cleaned = []
    for k in new_bs['variants']:
        v = new_bs['variants'][k]
        if isinstance(v, list):
            for m in v:
                cleaned = dict(m)
                if 'y' in cleaned:
                    del cleaned['y']
                if '_mirrored' in cleaned['model']:
                    cleaned['model'] = cleaned['model'].replace('_mirrored', '')
                if cleaned not in orig_cleaned:
                    orig_cleaned.append(cleaned)
                    simplified.append(m)
            new_bs['variants'][k] = simplified[0] if len(simplified) == 1 else simplified
    if new_bs != old_bs:
        new_states[os.path.basename(file)] = new_bs

blockstates = clip.directory('blockstates')
for k in new_states:
    json.dump(new_states[k], open('%s/%s' % (blockstates, k), 'w'), indent=2)
