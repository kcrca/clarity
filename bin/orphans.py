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

# Find all of our own models, and store them as possibly unused
for file in glob.glob('%s/block/*.json' % clip.directory('models')):
    model_file = subpath_re.search(file).group(1)
    unused_models[model_file] = True


def import_model(model_name):
    if model_name in models:
        return
    try:
        with open(os.path.join(clip.directory('models'), model_name + '.json')) as fp:
            model = json.load(fp)
    except IOError:
        with open(os.path.join(clip.directory('defaults', 'models'), model_name + '.json')) as fp:
            model = json.load(fp)
    models[model_name] = model
    try:
        del unused_models[model_name]
    except KeyError:
        pass

    try:
        import_model(model['parent'])
    except KeyError:
        pass


for state_name in blockstates:
    state = blockstates[state_name]
    for model_name in models_for(state):
        try:
            del unused_models[model_name]
        except KeyError:
            pass
        import_model(model_name)

print len(models)
print len(unused_models)
print '\n'.join(unused_models)
