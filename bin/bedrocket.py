import argparse
import pathlib
import sys

import pandas as pd

from clip import *


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


def file_map(pack):
    data = pd.read_excel(r'bedrocket.ods', sheet_name="block")
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


bin = directory('bin')
os.chdir(bin)

parser = argparse.ArgumentParser(description='Convert java resource pack to bedrock')
parser.add_argument('pack', metavar='file', type=pathlib.Path)

args = parser.parse_args()

files = file_map(args.pack)
print(len(files))

# os.walk
