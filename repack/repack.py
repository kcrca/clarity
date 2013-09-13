# coding=utf-8

import ConfigParser
import os
import re
import shutil
import sys
import copy

import Image


__author__ = 'arnold'

re_pat = re.compile(r'[][?*()\\+|]')
block_id_pat = re.compile(r'(\d+):?(\d*)')
target_opt_pat = re.compile(r'([^:]*):(.*)')
tile_spec_pat = re.compile(r'(\d+)x(\d+)(?:@(\d+),(\d+))?')
ctm_opt_pat = re.compile(r'([a-z_]*):?(.*)')
not_in_pack_pat = re.compile(r'^\.|\.(pxm|tiff)$')

warnings = []

#Copyright_©_2010-2013_Graham_Edgecombe._All_Rights_Reserved.
ids = {
    "air": "0",
    "stone": "1",
    "grass": "2",
    "grass_top": "2",
    "grass_side": "2",
    "grass_side_overlay": "2",
    "dirt": "3",
    "cobblestone": "4",
    "planks_oak": "5:0",
    "planks_spruce": "5:1",
    "planks_birch": "5:2",
    "planks_jungle": "5:3",
    "oak_sapling": "6:0",
    "spruce_sapling": "6:1",
    "birch_sapling": "6:2",
    "jungle_sapling": "6:3",
    "bedrock": "7",
    "water": "8",
    "stationary_water": "9",
    "lava": "10",
    "stationary_lava": "11",
    "sand": "12",
    "gravel": "13",
    "gold_ore": "14",
    "iron_ore": "15",
    "coal_ore": "16",
    "oak_wood": "17:0",
    "spruce_wood": "17:1",
    "birch_wood": "17:2",
    "jungle_wood": "17:3",
    "oak_leaves": "18:0",
    "spruce_leaves": "18:1",
    "birch_leaves": "18:2",
    "jungle_leaves": "18:3",
    "sponge": "19",
    "glass": "20",
    "lapis_ore": "21",
    "lapis_block": "22",
    "dispenser": "23",
    "sandstone_top": "24",
    "sandstone_normal": "24:0",
    "sandstone_carved": "24:1",
    "sandstone_smooth": "24:2",
    "note_block": "25",
    "bed_block": "26",
    "powered_rail": "27",
    "detector_rail": "28",
    "sticky_piston": "29",
    "web": "30",
    "tall_grass": "31:0",
    "fern": "31:1",
    "dead_shrub": "32",
    "piston": "33",
    "piston_head": "34",
    "wool_colored_white": "35:0",
    "wool_colored_orange": "35:1",
    "wool_colored_magenta": "35:2",
    "wool_colored_light_blue": "35:3",
    "wool_colored_yellow": "35:4",
    "wool_colored_lime": "35:5",
    "wool_colored_pink": "35:6",
    "wool_colored_gray": "35:7",
    "wool_colored_silver": "35:8",
    "wool_colored_cyan": "35:9",
    "wool_colored_purple": "35:10",
    "wool_colored_blue": "35:11",
    "wool_colored_brown": "35:12",
    "wool_colored_green": "35:13",
    "wool_colored_red": "35:14",
    "wool_colored_black": "35:15",
    "dandelion": "37",
    "rose": "38",
    "mushroom_block_skin_brown": "39",
    "mushroom_block_skin_red": "40",
    "gold_block": "41",
    "iron_block": "42",
    "double_stone_slab": "43:0",
    "double_sandstone_slab": "43:1",
    "double_wooden_slab": "43:2",
    "double_cobblestone_slab": "43:3",
    "double_brick_slab": "43:4",
    "double_stone_brick_slab": "43:5",
    "double_nether_brick_slab": "43:6",
    "double_quartz_slab": "43:7",
    "stone_slab": "44:0",
    "sandstone_slab": "44:1",
    "wooden_slab": "44:2",
    "cobblestone_slab": "44:3",
    "brick_slab": "44:4",
    "stone_brick_slab": "44:5",
    "nether_brick_slab": "44:6",
    "quartz_slab": "44:7",
    "brick": "45",
    "tnt": "46",
    "bookshelf": "47",
    "mossy_cobblestone": "48",
    "obsidian": "49",
    "torch": "50",
    "fire": "51",
    "monster_spawner": "52",
    "oak_wood_stairs": "53",
    "chest": "54",
    "redstone_wire": "55",
    "diamond_ore": "56",
    "diamond_block": "57",
    "workbench": "58",
    "wheat_crops": "59",
    "soil": "60",
    "furnace": "61",
    "burning_furnace": "62",
    "sign_post": "63",
    "wooden_door_block": "64",
    "ladder": "65",
    "rails": "66",
    "cobblestone_stairs": "67",
    "wall_sign": "68",
    "lever": "69",
    "stone_pressure_plate": "70",
    "iron_door_block": "71",
    "wooden_pressure_plate": "72",
    "redstone_ore": "73",
    "glowing_redstone_ore": "74",
    "redstone_torch_off": "75",
    "redstone_torch_on": "76",
    "stone_button": "77",
    "snow": "80",
    "ice": "79",
    "snow_block": "80",
    "cactus": "81",
    "clay": "82",
    "sugar_cane": "83",
    "jukebox": "84",
    "fence": "85",
    "pumpkin": "86",
    "netherrack": "87",
    "soul_sand": "88",
    "glowstone": "89",
    "portal": "90",
    "jack-o-lantern": "91",
    "cake_block": "92",
    "redstone_repeater_block_off": "93",
    "redstone_repeater_block_on": "94",
    "locked_chest": "95",
    "trapdoor": "96",
    "stone_silverfish": "97:0",
    "cobblestone_silverfish": "97:1",
    "stone_brick_silverfish": "97:2",
    "stone_brick": "98:0",
    "mossy_stone_brick": "98:1",
    "cracked_stone_brick": "98:2",
    "carved_stone_brick": "98:3",
    "red_mushroom_cap": "99",
    "brown_mushroom_cap": "100",
    "iron_bars": "101",
    "glass_pane": "102",
    "melon_block": "103",
    "pumpkin_stem": "104",
    "melon_stem": "105",
    "vines": "106",
    "fence_gate": "107",
    "brick_stairs": "108",
    "stone_brick_stairs": "109",
    "mycelium": "110",
    "mycelium_top": "110",
    "mycelium_side": "110",
    "lily_pad": "111",
    "nether_brick": "112",
    "nether_brick_fence": "113",
    "nether_brick_stairs": "114",
    "nether_wart": "115",
    "enchantment_table": "116",
    "brewing_stand": "117",
    "cauldron": "118",
    "end_portal": "119",
    "end_portal_frame": "120",
    "end_stone": "121",
    "dragon_egg": "122",
    "redstone_lamp_inactive": "123",
    "redstone_lamp_active": "124",
    "double_oak_wood_slab": "125:0",
    "double_spruce_wood_slab": "125:1",
    "double_birch_wood_slab": "125:2",
    "double_jungle_wood_slab": "125:3",
    "oak_wood_slab": "126:0",
    "spruce_wood_slab": "126:1",
    "birch_wood_slab": "126:2",
    "jungle_wood_slab": "126:3",
    "cocoa_plant": "127",
    "sandstone_stairs": "128",
    "emerald_ore": "129",
    "ender_chest": "130",
    "tripwire_hook": "131",
    "tripwire": "132",
    "emerald_block": "133",
    "spruce_wood_stairs": "134",
    "birch_wood_stairs": "135",
    "jungle_wood_stairs": "136",
    "command_block": "137",
    "beacon_block": "138",
    "cobblestone_wall": "139:0",
    "mossy_cobblestone_wall": "139:1",
    "flower_pot": "140",
    "carrots": "141",
    "potatoes": "142",
    "wooden_button": "143",
    "mob_head": "144",
    "anvil": "145",
    "trapped_chest": "146",
    "weighted_pressure_plate_light": "147",
    "weighted_pressure_plate_heavy": "148",
    "redstone_comparator_inactive": "149",
    "redstone_comparator_active": "150",
    "daylight_sensor": "151",
    "redstone_block": "152",
    "quartz_ore": "153",
    "hopper": "154",
    "quartz_block": "155:0",
    "quartz_block_side": "155:0",
    "quartz_block_top": "155:0",
    "quartz_block_bottom": "155:0",
    "carved_quartz_block": "155:1",
    "pillar_quartz_block": "155:2",
    "quartz_stairs": "156",
    "activator_rail": "157",
    "dropper": "158",
    "hardened_clay_stained_white": "159:0",
    "hardened_clay_stained_orange": "159:1",
    "hardened_clay_stained_magenta": "159:2",
    "hardened_clay_stained_light_blue": "159:3",
    "hardened_clay_stained_yellow": "159:4",
    "hardened_clay_stained_lime": "159:5",
    "hardened_clay_stained_pink": "159:6",
    "hardened_clay_stained_gray": "159:7",
    "hardened_clay_stained_silver": "159:8",
    "hardened_clay_stained_cyan": "159:9",
    "hardened_clay_stained_purple": "159:10",
    "hardened_clay_stained_blue": "159:11",
    "hardened_clay_stained_brown": "159:12",
    "hardened_clay_stained_green": "159:13",
    "hardened_clay_stained_red": "159:14",
    "hardened_clay_stained_black": "159:15",
    "hay_bale": "170",
    "white_carpet": "171:0",
    "orange_carpet": "171:1",
    "magenta_carpet": "171:2",
    "light_blue_carpet": "171:3",
    "yellow_carpet": "171:4",
    "lime_carpet": "171:5",
    "pink_carpet": "171:6",
    "gray_carpet": "171:7",
    "light_gray_carpet": "171:8",
    "cyan_carpet": "171:9",
    "purple_carpet": "171:10",
    "blue_carpet": "171:11",
    "brown_carpet": "171:12",
    "green_carpet": "171:13",
    "red_carpet": "171:14",
    "black_carpet": "171:15",
    "hardened_clay": "172",
    "coal_block": "173",
}


class Change(object):
    def __init__(self):
        self.use_override = False

    def apply(self, src, dst, subpath):
        print "%s -> %s" % (self.name(), subpath)
        src_img = Image.open(src).convert('RGBA')
        self.do_change(dst, src_img)

    def do_change(self, dst, src_img):
        pass

    def name(self):
        return self.__class__.__name__.replace('Change', '')

    def set_options(self, opt_str):
        raise SyntaxError('%s: No options allowed' % self.name())

    def modified(self, opt_str):
        m = copy.deepcopy(self)
        m.set_options(opt_str)
        return m


class CopyChange(Change):
    def apply(self, src, dst, subpath):
        shutil.copy2(src, dst)


class SimpleChange(Change):
    def do_change(self, dst, src_img):
        dst_img = Image.new('RGBA', src_img.size)
        self.simple_change(src_img, dst_img)
        dst_img.save(dst)

    def simple_change(self, src_img, dst_img):
        pass


class MaskChange(SimpleChange):
    def __init__(self, mask_name):
        super(MaskChange, self).__init__()
        self.mask_name = mask_name
        mask_file = os.path.join(config_dir, 'masks', '%s.png' % mask_name)
        self.img = Image.open(mask_file)

    def name(self):
        return 'Mask %s' % self.mask_name

    def simple_change(self, src_img, dst_img):
        dst_img.paste(src_img, self.img)


class EraseEdgeChange(SimpleChange):
    def __init__(self, dup_size=None):
        super(SimpleChange, self).__init__()
        self.dup_size = dup_size

    def set_options(self, opt_str):
        if len(opt_str):
            self.dup_size = int(opt_str)

    def simple_change(self, src_img, dst_img):
        dst_img.paste(src_img)

        w, h = src_img.size
        b = h - 1 # index of bottom row
        e = w - 1 # index of end column
        copy_start = 0

        dup_size = self.dup_size
        if dup_size is not None:
            copy_start = (src_img.size[0] - dup_size) / 2
            copy_width = dup_size
        else:
            copy_start = 1
            copy_width = src_img.size[0] - 2

        copy_end = copy_start + copy_width

        def copy_row(row_from, row_to):
            t = src_img.crop((copy_start, row_from, copy_end, row_from + 1))
            if dup_size is None:
                dst_img.paste(t, (0, row_to)) # set the leftmost pixel
                dst_img.paste(t, (2, row_to)) # set the rightmost pixel
            dst_img.paste(t, (copy_start, row_to))

        def copy_col(col_from, col_to):
            t = src_img.crop((col_from, copy_start, col_from + 1, copy_end))
            dst_img.paste(t, (col_to, copy_start))


        copy_row(1, 0) # set the top row from its neighbor
        copy_row(b - 1, b) # set the bottom row from its neighbor
        copy_col(1, 0) # set the left row from its neighbor
        copy_col(e - 1, e) # set the right row form its neighbor


class TileOverEdge(SimpleChange):
    def __init__(self):
        super(SimpleChange, self).__init__()
        self.tile_size = None

    def set_options(self, opt_str):
        m = tile_spec_pat.match(opt_str)
        groups = m.groups()
        self.tile_size = tuple(int(s) for s in groups[0:2])
        self.tile_pos = (0, 0)
        if len(groups[3]):
            self.tile_pos = tuple(int(s) for s in groups[2:4])

    def simple_change(self, src_img, dst_img):
        if self.tile_size:
            size = self.tile_size
            pos = self.tile_pos
        else:
            size = tuple(((i - 2) / 4) * 4 for i in src_img.size)
            pos = (1, 1)

        w, h = size

        tile = src_img.crop((pos[0], pos[1], pos[0] + w, pos[1] + h))
        for x in range(0, src_img.size[0], w):
            x_end = x + w
            for y in range(0, src_img.size[1], h):
                y_end = y + h
                if x_end >= src_img.size[0] or y_end >= src_img.size[1]:
                    use_tile = tile.crop((0, 0, src_img.size[0] - x,
                                          src_img.size[1] - y))
                else:
                    use_tile = tile
                box = (x, y)
                dst_img.paste(use_tile, box)
                # dst_img.paste(tile, (0, 0))
                # tile = src_img.crop((3, 1, 5, b))
                # dst_img.paste(tile, (e - 1, 0))
                # tile = dst_img.crop((0, 2, w, 4))
                # dst_img.paste(tile, (0, b - 1))


change_by_name = {
    'erase_edge': EraseEdgeChange(),
    'tile_over_edge': TileOverEdge()}


class ConnectedTextureChange(Change):
    def __init__(self, template_name):
        super(Change, self).__init__()
        self.template_name = template_name
        self.template_dir = '%s/ctm_templates/%s' % (config_dir, template_name)
        self.use_override = True
        self.edgeless_change = change_by_name['erase_edge']
        self.edgeless_change_opt = ''

    def name(self):
        return 'CTM(%s)' % self.template_name

    def set_options(self, opt_str):
        if len(opt_str):
            m = ctm_opt_pat.match(opt_str)
            ch, ch_opt = m.groups()
            if ch:
                self.edgeless_change = change_by_name[ch]
            if len(ch_opt):
                self.edgeless_change_opt = ch_opt

    def do_change(self, dst, src_img):
        ctm_top_dir = os.path.join(inner_top, 'mcpatcher', 'ctm')
        if not os.path.isdir(ctm_top_dir):
            os.makedirs(ctm_top_dir)

        base = os.path.basename(dst)[:-4]
        block_id_str = ids[base]
        block_id, block_dmg = block_id_pat.match(block_id_str).groups()
        ctm_dir = os.path.join(ctm_top_dir, base)

        edgeless_img = Image.new('RGBA', src_img.size)
        edgeless_change = self.edgeless_change
        if len(self.edgeless_change_opt):
            edgeless_change = edgeless_change.modified(self.edgeless_change_opt)
        edgeless_change.simple_change(src_img, edgeless_img)

        mask_sides = lambda src, dst: self._mask_block(src, dst, src_img,
                                                       edgeless_img)
        copytree(self.template_dir, ctm_dir, ignore=only_png,
                 copy_function=mask_sides)

        prop_file = os.path.join(ctm_dir, 'block%s.properties' % block_id)
        template_props = os.path.join(self.template_dir, 'block.properties')
        with open(template_props) as t:
            with open(prop_file, mode='w') as o:
                o.writelines(t)
                if len(block_dmg):
                    o.write('metadata=%s\n' % block_dmg)


    def _mask_block(self, src, dst, block_img, edgeless_img):
        # block_img.show()
        mask_img = Image.open(src).convert('RGBA')
        # mask_img.show()
        dst_img = edgeless_img.copy()
        dst_img.paste(block_img, mask_img)
        dst_img.save(dst)
        # dst_img.show()
        return


class Pass(object):
    def __init__(self):
        self.change_for = {}
        self.re_changes = []
        self.default_change = None

    def set_change(self, target, change):
        m = target_opt_pat.match(target)
        if m:
            target, opt_str = m.groups()
            change = change.modified(opt_str)
        re = self._target_re(target)
        if re:
            self.re_changes.append((re, change))
        else:
            path = target + '.png'
            if path in self.change_for:
                existing = self.change_for[target]
                print 'Duplicate change for %s: %s and %s' % (
                    target, change.name(), existing.name())
            else:
                self.change_for[path] = change

    def _find_change(self, path):
        path_png = path + '.png'

        # look for exact match of name
        k = None
        if path in self.change_for:
            k = path
        elif path_png in self.change_for:
            k = path_png
        if k:
            self.unused_changes.remove(k)
            return self.change_for[k]

        # look for pattern match
        for (re, change) in self.re_changes:
            k = None
            if re.search(path):
                k = path
            elif re.search(path_png):
                k = path_png
            if k:
                try:
                    self.unused_changes.remove(re.pattern)
                except KeyError:
                    pass
                return change

        return None

    def run(self):
        self.unused_changes = set(
            self.change_for.keys() + [p[0].pattern for p in self.re_changes])
        copytree(src_dir, dst_dir, ignore=only_pack_files,
                 copy_function=self.change, overlay=True)
        if len(self.unused_changes):
            global warnings
            warnings += ('Changes not done: Files not found: %s' % ', '.join(
                self.unused_changes),)


    def change(self, src, dst):
        dst, subpath = subpath_for(dst)
        change = self._find_change(subpath)
        if not change and dst[:inner_top_len] == inner_top:
            base = dst[inner_top_len + 1:]
            change = self._find_change(base)
        if not change and dst[:texture_dir_len] == texture_dir:
            base = os.path.basename(dst)
            change = self._find_change(base)
        if not change:
            change = self.default_change
        if not change:
            return
        override = os.path.join(overrides_dir, subpath)
        if os.path.isfile(override):
            if change.use_override:
                print '%s: using overridden file: %s' % (
                    change.name(), override)
                src = override
            else:
                print '%s ignored: %s (overridden)' % (change.name(), subpath)
                return
        change.apply(src, dst, subpath)

    def _target_re(self, target):
        if re_pat.search(target):
            return re.compile(target + '.png')
        return None


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


config = ConfigParser.SafeConfigParser()

src_dir, dst_dir = sys.argv[1:]
try:
    config_dir = sys.argv[3]
except:
    config_dir = dst_dir + '.repack'
src_dir = normpath(src_dir)
dst_dir = normpath(dst_dir)

config.read(os.path.join(config_dir, 'repack.cfg'))

if os.path.isdir(dst_dir):
    shutil.rmtree(dst_dir)

inner_top = normpath('%s/assets/minecraft' % dst_dir)
inner_top_len = len(inner_top)
texture_dir = normpath('%s/textures/blocks/' % inner_top)
texture_dir_len = len(texture_dir)
overrides_dir = normpath('%s/override' % config_dir)

passes = (Pass(), Pass())

passes[0].default_change = CopyChange()

try:
    for mask_name, targets in config.items('masks'):
        change = MaskChange(mask_name)
        for target in targets.split():
            passes[0].set_change(target, change)
except ConfigParser.NoSectionError:
    pass

try:
    for change_name, targets in config.items('changes'):
        change = change_by_name[change_name]
        for target in targets.split():
            passes[0].set_change(target, change)
except ConfigParser.NoSectionError:
    pass

try:
    for template_name, targets in config.items('ctm'):
        change = ConnectedTextureChange(template_name)
        for target in targets.split():
            passes[1].set_change(target, change)
except ConfigParser.NoSectionError:
    pass


# This is copied from shutil, because I need the copy_function option which
# wasn't added until 3.3 or so. Sigh.

# Also added option to overlay on target instead of removing it

def copytree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2,
        overlay=False):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    try:
        os.makedirs(dst)
    except OSError:
        if not overlay:
            raise

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, copy_function,
                         overlay)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if shutil.WindowsError is not None and isinstance(why,
                                                          shutil.WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors


def subpath_for(dst):
    dst = normpath(dst)
    subpath = dst[len(dst_dir) + 1:]
    return dst, subpath


def only_pack_files(directory, files):
    return [f for f in files if f[0] == '.']


def only_png(directory, files):
    return [f for f in files if f[-4:] != '.png']


def verbose_copy(src, dst):
    dst, subpath = subpath_for(dst)
    if os.path.isfile(src):
        action = "overriding" if os.path.exists(dst) else "adding"
        print "%s: %s" % (action, subpath)
    shutil.copy2(src, dst)


for p in passes:
    p.run()

if os.path.exists(overrides_dir):
    copytree(overrides_dir, dst_dir, ignore=only_pack_files,
             copy_function=verbose_copy,
             overlay=True)

print '\n'.join(warnings)
