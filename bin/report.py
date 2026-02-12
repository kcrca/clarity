#!/usr/bin/env python3

# Generates a report comparing two packs.

import configparser
import glob
import re
import subprocess
import sys
from pathlib import Path

import clip
from clip import *

__author__ = 'arnold'

status_by_name = {}


def orphans():
    def find_models(data) -> set:
        models = set()
        if data is None:
            pass
        elif isinstance(data, list):
            for member in data:
                models.update(find_models(member))
        elif isinstance(data, dict):
            if 'model' in data and isinstance(data['model'], str):
                models.add(data['model'])
            for key in data:
                models.update(find_models(data[key]))
        return models

    def find_textures(data) -> set:
        textures = set()
        try:
            textures_block = data['textures']
            for texture_name in textures_block:
                texture = path_part(textures_block[texture_name])
                if re.search('^[a-z]', texture):
                    textures.add(texture)
        except KeyError:
            pass
        return textures

    def models_for(state) -> set:
        return find_models(state)

    def path_part(model_name):
        # Sometimes texture is {'sprite': ...}
        if isinstance(model_name, dict):
            model_name = model_name['sprite']
        return model_name.replace('minecraft:', '')

    def import_model(model_name):
        model_name = path_part(model_name)
        if model_name in models:
            return
        if model_name.startswith('builtin/'):
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
            for o in model['overrides']:
                if 'model' in o:
                    import_model(o['model'])
        except KeyError:
            pass

        try:
            import_model(model['parent'])
        except KeyError:
            pass

    subpath_re = re.compile(r'((item|block)/.*)\.[a-z]+$')
    roots = {}
    root_names = {'blockstates': 'block', 'items': 'item'}
    models = {}
    unused_models = {}
    source_files = {}
    # First we pull in all the models for the blocks, using the blockstates and items files as the roots of the tree.
    # We overwrite any info from the default models with our own.
    for root, base in root_names.items():
        for file in glob.glob('%s/*.json' % clip.directory('defaults', root)):
            path = f'{base}/{os.path.basename(file)}'
            source_files[path] = file
        for file in glob.glob('%s/*.json' % clip.directory(root)):
            path = f'{base}/{os.path.basename(file)}'
            source_files[path] = file
    # Now load the files
    for path in source_files:
        with open(source_files[path]) as fp:
            roots[path] = json.load(fp)
    # Find all of our own models, and store them as possibly unused
    for file in glob.glob('%s/**/*.json' % clip.directory('models'), recursive=True):
        m = subpath_re.search(file)
        model_name = m.group(1)
        unused_models[model_name] = True
    for root in roots:
        model = roots[root]
        used_models = models_for(model)
        for model_name in used_models:
            model_name = path_part(model_name)
            try:
                del unused_models[model_name]
            except KeyError:
                pass
            import_model(model_name)
    # Now lets look for unused textures
    textures = set()
    unused_textures = set()
    # bookshelf images are only _probably_ used, so this allows for the case where one isn't
    for file in glob.glob('%s/item/*.png' % clip.directory('textures')) + glob.glob(
            '%s/block/*.png' % clip.directory('textures')):
        texture_name = subpath_re.search(file).group(1)
        if not Path(file + '.split').exists():
            unused_textures.add(texture_name)
    for model_name in models:
        model = models[model_name]
        for texture_name in find_textures(model):
            # print '%s: %s' % (model_name, texture_name)
            textures.add(texture_name)
            try:
                unused_textures.remove(texture_name)
            except KeyError:
                pass

    for m in unused_models:
        unused_checker.add_path([], f'models/{m}.json')
    for m in unused_textures:
        unused_checker.add_path([], f'textures/{m}.png')
    return models, textures


# noinspection PyUnusedLocal
def no_path(groups):
    return None


def whole_match(groups):
    assert len(groups) == 1
    return groups[0]


def first_group(groups):
    assert len(groups) == 2
    return groups[0]


def path_from_only(groups):
    assert len(groups) == 2
    if len(groups[0]) > 0:
        path = os.path.join(groups[0], groups[1])
    else:
        path = groups[1]
    return path


class FileStatus(object):
    def __init__(self, prefix, pattern, path_from_groups=whole_match):
        self.pat = re.compile(pattern)
        self.prefix = prefix
        self.files = set()
        self.ignore = []
        self.unused_ignores = set()
        self.path_from_groups = path_from_groups
        self.multi_matches = dict()
        try:
            to_ignore = config.get('ignore', prefix.lower())
            to_split = re.sub(r'[ \t]*#[^\n]*', '', to_ignore)
            pats = set(to_split.split())
            self.ignore = []
            for pat in pats:
                self.ignore.append(re.compile(pat))
            self.unused_ignores |= pats
        except configparser.NoOptionError:
            pass
        status_by_name[self.prefix] = self

    def status_match(self, line):
        m = self.pat.search(line)
        if m:
            groups = m.groups()
            path = self.path_from_groups(groups) if len(groups) else None
            self.add_path(groups, path)
        return m

    def dump(self):
        if self.files:
            print(self.prefix)
            for f in sorted(self.files):
                print(f'    {f}')
        if len(self.unused_ignores) > 0:
            print('  UNUSED pattern:', ', '.join(sorted(self.unused_ignores)))
        if len(self.multi_matches) > 0:
            print('  MULTIPLE pattern matches for path:')
            for p in sorted(self.multi_matches):
                print('    %s: %s' % (p, ', '.join(self.multi_matches[p])))

    def add_path(self, groups, path):
        """
        Add the given path to list of matches for this path UNLESS it matches the patterns to be ignored.
        """
        if not path:
            return
        patterns = []
        for pat in self.ignore:
            if pat.search(path):
                patterns.append(pat.pattern)
                self.unused_ignores.discard(pat.pattern)
        if len(patterns) == 0:
            self.files.add(path)
        elif len(patterns) > 1:
            self.multi_matches[path] = patterns


# This does an extra check for changed PNG files to see if they are really different
def frame_cnt(img_file, img):
    try:
        meta_path = Path(img_file + '.mcmeta')
        with open(meta_path) as fp:
            mcmeta = json.load(fp)
            frames = mcmeta['animation']['frames']
            frames = map(lambda x: x if isinstance(x, int) else x['index'], frames)
            return len(set(frames))

    except KeyError:
        if 'animation' in mcmeta:
            return int(img.size[1] / img.size[0])
        else:
            return 1
    except FileNotFoundError:
        return 1


class ReshapedFileStatus(FileStatus):
    def __init__(self, prefix, pattern):
        super().__init__(prefix, pattern)


class OnlyInFileStatus(FileStatus):
    def reachable(self, groups, name):
        # Fles in our {textures,models}/{blocks,items} should be reachable from a model in {blockstates,items}. The
        # question is what to do with those that aren't. Some are used by other tools. I think it will be fine to use
        # patterns to suppress these. If it becomes a problem, we can invent some easy pattern(s) for tool-only file
        # names.
        if m := re.search('^(textures|models)/(item|block)', name):
            source = models if m.group(1) == 'models' else textures
            full_suffix = ''.join(Path(name).suffixes)
            return name[len(m.group(1)) + 1:-len(full_suffix)] in source
        return self.default_reachable()

    def default_reachable(self):
        return True

    def add_path(self, groups, name):
        # These are things that can't be suppressed with simple RE checks
        if name.endswith('.mcmeta') and Path(name[:-len('.mcmeta')]).exists():
            return
        if name.endswith('.png') and Path(name + '.split').exists():
            return

        if not self.reachable(groups, name):
            super().add_path(groups, name)


class AddedFileStatus(OnlyInFileStatus):
    def default_reachable(self):
        return False


class ChangedFileStatus(FileStatus):
    def __init__(self, prefix, pattern, same_file_status, reshaped_file_status):
        super().__init__(prefix, pattern, first_group)
        self.same_file_status = same_file_status
        self.reshaped_file_status = reshaped_file_status

    def image_same(self, groups):
        img1 = Image.open(groups[0])
        img2 = Image.open(groups[1])

        frame_cnt1 = frame_cnt(groups[0], img1)
        frame_cnt2 = frame_cnt(groups[1], img2)
        ratio1 = img1.size[0] / (img1.size[1] / frame_cnt1)
        ratio2 = img2.size[0] / (img2.size[1] / frame_cnt2)
        if ratio1 != ratio2:
            # This is a different kind of error -- if the size ratios are different, that may need to be addressed
            self.reshaped_file_status.add_path(groups, groups[0])
            return False

        if img1.size != img2.size:
            return False
        pixels1 = img1.convert('RGBA').load()
        pixels2 = img2.convert('RGBA').load()
        for x in range(0, img1.size[0]):
            for y in range(0, img1.size[1]):
                if pixels1[(x, y)] != pixels2[(x, y)]:
                    return False
        return True

    def add_path(self, groups, path):
        if path.endswith('.png'):
            # Check if they are equivalent images, just encoded differently.
            if self.image_same(groups):
                self.same_file_status.add_path(groups, path)
                return
        super().add_path(groups, path)


class MissingFileStatus(OnlyInFileStatus):
    def reachable(self, groups, name):
        # For files that are only in the other pack, the sense of "reachability" is inverted -- files that are not
        # reachable are ignorable. As a heuristic, models don't matter here because there are many original models
        # that we don't use, so we just view all models as reachable.
        if name.startswith('models'):
            return True
        reachable = super().reachable(groups, name)
        return not reachable


config_file = directory('config', 'report_default.cfg')
if len(sys.argv) > 1:
    config_file = sys.argv[1]

config = configparser.ConfigParser()
config.read(config_file)
unused_checker = FileStatus('Unused', '')

os.chdir(directory('minecraft'))

models, textures = orphans()
print('Models: %s' % len(models))
print('Textures: %d' % len(textures))
unused_checker.dump()

other = config.get('basic', 'top')
other_esc = other.replace('.', '\\.')

same_checker = FileStatus('Same', r'^Files (?:\./)?(.*) and .* identical', path_from_groups=no_path)
reshaped_checker = FileStatus('Reshaped', '')

statuses = (
    FileStatus('Ignored', r'\.swp|\~|\/.$|\.DS_Store|_diff\.gif$', path_from_groups=whole_match),
    same_checker,
    ChangedFileStatus('Changed', r'^Files (?:\./)?(.*) and ([^\s]*) differ', same_checker, reshaped_checker),
    MissingFileStatus('Missing', r'^Only in ' + other_esc + '/?(.*): (.*)', path_from_groups=path_from_only),
    AddedFileStatus('Added', r'^Only in \./?(.*): (.*)', path_from_groups=path_from_only),
)

diff = subprocess.Popen(['diff', '-rsq', '.', other], stdout=subprocess.PIPE)

irrelevant_re = re.compile(r'^[0-9<>-]')

for line in diff.stdout:
    line = line.decode('utf-8')
    if not irrelevant_re.search(line):
        for status in statuses:
            if status.status_match(line):
                break

print_order = ['Missing', 'Added', 'Same', 'Changed', 'Reshaped']

for name in print_order:
    status = status_by_name[name]
    status.dump()
