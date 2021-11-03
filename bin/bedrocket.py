import argparse
import pathlib

import pandas as pd

from clip import *


def do_ignore(path, contents):
    if path in skip_dirs:
        return contents
    return ignore_glob(path, contents)


def as_path(param, default_loc):
    if type(param) != str:
        return None
    if len(param) == 0:
        return None
    if param == 'n/a':
        return None
    if param[0] == '/':
        return param
    return default_loc + '/' + param


def file_map():
    data = pd.read_excel(directory('config') + '/bedrocket.ods', sheet_name="block")
    file_cols = data[['Java (Vanilla)', 'Bedrock']]
    files = {'/pack.png': '/pack_icon.png'}

    j_block_dir = '/assets/minecraft/textures/block'
    b_block_dir = '/textures/blocks'

    for row in file_cols.itertuples():
        j = as_path(row[1], j_block_dir)
        b = as_path(row[2], b_block_dir)
        if j and b:
            files[j] = b

    return files


def do_skip(path, _):
    return path in skip_dirs


def do_copy(src, dst):
    print('copy %s %s' % (src, dst))
    return True


parser = argparse.ArgumentParser(description='Convert java resource pack to bedrock')
parser.add_argument('java_pack', type=pathlib.Path)
parser.add_argument('bedrock_pack', type=pathlib.Path)

args = parser.parse_args()
java_pack = str(args.java_pack)
bedrock_pack = str(args.bedrock_pack)
skip_dirs = set()
ignore_glob = shutil.ignore_patterns('.*')
for s in ('assets/minecraft/blockstates', 'assets/minecraft/optifine'):
    skip_dirs.add(java_pack + '/' + s)

files = file_map()
print(len(files))

if args.bedrock_pack.exists():
    shutil.rmtree(args.bedrock_pack)
shutil.copytree(java_pack, bedrock_pack, ignore=do_ignore, copy_function=do_copy, symlinks=True)
