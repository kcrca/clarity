import os

__author__ = 'arnold'

import glob
import json
import clip
import re


def find_models(state):
    if state is None:
        return []

    if isinstance(state, list):
        models = []
        for member in state:
            models += find_models(member)
        return models

    if isinstance(state, dict):
        try:
            return (state['model'],)
        except KeyError:
            pass
        models = []
        for key in state:
            models += find_models(state[key])
        return models

    return []


def models_for(state):
    return find_models(state)

    try:
        variants = state['variants']
        models += models_under(variants)[:]
    except KeyError:
        pass

    try:
        for part in state['multipart']:
            v = part['apply']
            models += models_under(v)[:]
            print type(v)
    except KeyError:
        pass

    return models


def models_under(variants):
    models = []
    for variant_key in variants:
        v = variants[variant_key]
        print type(v)
        if isinstance(v, list):
            for variant in v:
                try:
                    models += (variant['model'],)
                except KeyError:
                    pass
        else:
            try:
                models += (v['model'],)
            except KeyError:
                pass
        try:
            models += (variants['model'],)
        except KeyError:
            pass
    return models


subpath_re = re.compile(r'([^/]+/[^/]+)\.json$')

blockstates = {}

for file in glob.glob('%s/*.json' % clip.directory('defaults', 'blockstates')):
    with open(file) as fp:
        blockstates[os.path.basename(file)] = json.load(fp)

for file in glob.glob('%s/*.json' % clip.directory('blockstates')):
    with open(file) as fp:
        blockstates[os.path.basename(file)] = json.load(fp)

# Item models have nothing that refers to them. One of our item models is unused if there is no
# corresponding item model in the defaults

models = {}
unused_models = {}

default_models = clip.directory('defaults', 'models')

for file in glob.glob('%s/block/*.json' % clip.directory('models')):
    model_file = subpath_re.search(file).group(1)
    unused_models[model_file] = True

for state_name in blockstates:
    state = blockstates[state_name]
    for model in models_for(state):
        try:
            del unused_models[model]
        except KeyError:
            pass
        models[model] = True

print len(models)
print len(unused_models)
print '\n'.join(unused_models)
