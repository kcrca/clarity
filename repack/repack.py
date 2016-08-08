# coding=utf-8

import ConfigParser
import os
import re
import shutil
import copy

import Image
import errno

import ImageDraw

__author__ = 'arnold'

re_re = re.compile(r'[][?*()\\+|]')
block_id_re = re.compile(r'(\d+):?([\d]*)')
target_opt_re = re.compile(r'([^:]*):(.*)')
tile_spec_re = re.compile(r'(\d+)x(\d+)(?:@(\d+),(\d+))?')
ctm_opt_re = re.compile(r'(\d+):?([\d&]+)?')
skip_dirs_re = re.compile(r'^\.|^\.?[a-z]$')
do_not_copy_re = re.compile(r'\.(py|cfg|sh|pxm|config|tiff)$|/(.|\.DS_Store|\..|\.gitignore)$')

warnings = []


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


core = normpath('core')
continuity = normpath('continuity')
connectivity = normpath('connectivity')


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

    def set_options(self, label, opt_str):
        raise SyntaxError('%s: No options allowed' % self.name())

    def modified(self, label, opt_str):
        m = copy.deepcopy(self)
        m.set_options(label, opt_str)
        return m


class CopyChange(Change):
    def apply(self, src, dst, subpath):
        if not do_not_copy_re.search(dst):
            shutil.copy2(src, dst)


class SimpleChange(Change):
    def do_change(self, dst, src_img):
        dst_img = Image.new('RGBA', src_img.size)
        self.simple_change(src_img, dst_img)
        dst_img.save(dst)

    def simple_change(self, src_img, dst_img):
        pass


class EraseEdgeChange(SimpleChange):
    def __init__(self, dup_size=None):
        super(SimpleChange, self).__init__()
        self.dup_size = dup_size

    def set_options(self, label, opt_str):
        if len(opt_str):
            self.dup_size = int(opt_str)

    def simple_change(self, src_img, dst_img):
        dst_img.paste(src_img)

        w, h = src_img.size
        b = h - 1  # index of bottom row
        e = w - 1  # index of end column
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
                dst_img.paste(t, (0, row_to))  # set the leftmost pixel
                dst_img.paste(t, (2, row_to))  # set the rightmost pixel
            dst_img.paste(t, (copy_start, row_to))

        def copy_col(col_from, col_to):
            t = src_img.crop((col_from, copy_start, col_from + 1, copy_end))
            dst_img.paste(t, (col_to, copy_start))

        copy_row(1, 0)  # set the top row from its neighbor
        copy_row(b - 1, b)  # set the bottom row from its neighbor
        copy_col(1, 0)  # set the left row from its neighbor
        copy_col(e - 1, e)  # set the right row form its neighbor


class TileOverEdge(SimpleChange):
    def __init__(self):
        super(SimpleChange, self).__init__()
        self.tile_size = None
        self.tile_pos = None

    def set_options(self, label, opt_str):
        m = tile_spec_re.match(opt_str)
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

mask_cache = {}


def _mask_block(mask, dst, block_img, edgeless_img):
    assert block_img.size == edgeless_img.size

    # block_img.show()
    key = (mask, block_img.size[0])
    try:
        mask_img = mask_cache[key]
    except KeyError:
        mask_img = Image.open(mask).convert('RGBA')
        # mask_img.show()
        if mask_img.size != block_img.size:
            mask_img = rescale_mask(mask_img, block_img.size)
        mask_cache[key] = mask_img

    dst_img = edgeless_img.copy()
    dst_img.paste(block_img, mask_img)
    dst_img.save(dst)
    # dst_img.show()
    return


def rescale_mask(o_mask, img_size):
    assert o_mask.size[0] == o_mask.size[1]
    assert img_size[0] == img_size[1]
    n_mask = o_mask.resize(img_size)
    o_size = o_mask.size[0]
    n_size = img_size[0]
    scale = n_size / o_size
    assert scale > 1
    draw = ImageDraw.Draw(n_mask)
    draw.rectangle((1, 1, n_size - 2, n_size - 2), fill=(0, 0, 0, 0))
    del draw

    bar = n_mask.crop((scale, 0, 2 * scale - 1, n_size))
    n_mask.paste(bar, (1, 0))
    n_mask.paste(bar, (n_size - scale, 0))
    bar = n_mask.crop((0, scale, n_size, 2 * scale - 1))
    n_mask.paste(bar, (0, 1))
    n_mask.paste(bar, (0, n_size - scale))

    return n_mask


class ConnectedTextureChange(Change):
    def __init__(self, template_name, ctm_pass):
        super(Change, self).__init__()
        self.ctm_pass = ctm_pass
        self.template_name = template_name
        self.template_dir = os.path.join(ctm_pass.template_top, template_name)
        self.use_override = True
        self.id_specs = ()

    def name(self):
        return 'CTM(%s)' % self.template_name

    def set_options(self, label, opt_str):
        if len(opt_str):
            self.id_specs = opt_str.split(',')
        else:
            raise SyntaxError('No data specified for %s' % label)

    def apply(self, src, dst, subpath):
        CopyChange().apply(src, dst, subpath)
        super(ConnectedTextureChange, self).apply(src, dst, subpath)

    def do_change(self, dst, src_img):
        ctm_top_dir = os.path.join(self.ctm_pass.dst_assets_dir, 'mcpatcher', 'ctm')
        safe_mkdirs(ctm_top_dir)

        base = os.path.basename(dst)[:-4]
        ctm_dir = os.path.join(ctm_top_dir, base)

        edgeless = os.path.join(self.ctm_pass.edgeless_block_dir, base + '.png')
        edgeless_img = Image.open(edgeless).convert('RGBA')
        copytree(self.template_dir, ctm_dir, ignore=only_png, overlay=True,
                 copy_function=lambda src_path, dst_path: _mask_block(src_path, dst_path, src_img, edgeless_img))

        for id_spec in self.id_specs:
            block_id, block_dmg = block_id_re.match(id_spec).groups()
            if not block_id:
                raise SyntaxError('%s: Invalid block ID spec: "%s"' % (base, id_spec))
            prop_file = os.path.join(ctm_dir, 'block%s.properties' % block_id)
            template_props = os.path.join(self.template_dir, 'block.properties')
            with open(template_props) as t:
                with open(prop_file, mode='w') as o:
                    if len(block_dmg):
                        o.write('metadata=%s\n' % block_dmg)
                    o.writelines(t)

    def modified(self, label, opt_str):
        # Must remove ctm_pass before deep copy or we copy too much -- it is the one thing we don't want to deep copy
        # (looked at overriding __deepcopy__(memo) but it seemed more complicated, not less
        ctm_pass = self.ctm_pass
        self.ctm_pass = None
        m = super(ConnectedTextureChange, self).modified(label, opt_str)
        self.ctm_pass = ctm_pass
        m.ctm_pass = ctm_pass
        return m


def safe_mkdirs(dst_dir):
    try:
        os.mkdir(dst_dir)
    except os.error, e:
        if e.errno != errno.EEXIST:
            raise


def _target_re(target):
    if re_re.search(target):
        return re.compile(target + '.png')
    return None


class Pass(object):
    def __init__(self, src_name, dst_name):
        self.change_for = {}
        self.re_changes = []
        self.default_change = CopyChange()
        self.src_top = normpath(src_name)
        self.dst_top = normpath(dst_name)
        self.repack_dir = self.dst_top + '.repack'
        self.override_top = os.path.join(self.repack_dir, 'override')
        self.dst_assets_dir = os.path.join(self.dst_top, 'assets', 'minecraft')
        self.dst_assets_dir_len = len(self.dst_assets_dir)
        self.dst_blocks_dir = os.path.join(self.dst_assets_dir, 'textures', 'blocks')
        self.dst_blocks_dir_len = len(self.dst_blocks_dir)
        self.src_blocks_dir = self.dst_blocks_dir.replace(self.dst_top, self.src_top)
        self.change_for = {}
        self.re_changes = []
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.join(self.repack_dir, 'repack.cfg'))
        self.parse_config(config)
        self.unused_changes = set(
            self.change_for.keys() + [c[0].pattern for c in self.re_changes])

    def parse_config(self, config):
        pass

    def record_change(self, subpath):
        pass

    def set_change(self, target, change):
        m = target_opt_re.match(target)
        if m:
            target, opt_str = m.groups()
            change = change.modified(target, opt_str)
        regexp = _target_re(target)
        if regexp:
            self.re_changes.append((regexp, change))
        else:
            path = target + '.png'
            if path in self.change_for:
                existing = self.change_for[path]
                print 'Duplicate change for %s: %s and %s' % (
                    target, change.name(), existing.name())
                os.sys.exit(1)
            else:
                self.change_for[path] = change

    def _find_change(self, path_png):
        if path_png.endswith('.png'):
            path = path_png[:-4]
        else:
            return None

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
        for (regexp, change) in self.re_changes:
            k = None
            if regexp.search(path):
                k = path
            elif regexp.search(path_png):
                k = path_png
            if k:
                try:
                    self.unused_changes.remove(regexp.pattern)
                except KeyError:
                    pass
                return change

        return None

    def run(self):
        for dir_name, subdir_list, file_list in os.walk(self.src_top):
            file_list = [f for f in file_list if not do_not_copy_re.match(f)]
            subdir_list = [f for f in subdir_list if not do_not_copy_re.match(f)]
            src_dir = dir_name
            dst_dir = dir_name.replace(self.src_top, self.dst_top)
            safe_mkdirs(dst_dir)
            for f in file_list:
                src = os.path.join(src_dir, f)
                dst = os.path.join(dst_dir, f)
                override = src.replace(self.src_top, self.override_top)
                if os.path.exists(override):
                    if len(only_pack_files(src_dir, [dst, ])) == 0:
                        shutil.copy(override, dst)
                else:
                    self.change(src, dst)
        if len(self.unused_changes):
            global warnings
            warnings += (self.__class__.__name__ + 'Changes not done: Files not found: %s' % ', '.join(
                self.unused_changes),)

    def subpath_for(self, dst):
        dst = normpath(dst)
        subpath = dst[len(self.dst_top) + 1:]
        return dst, subpath

    def change(self, src, dst):
        dst, subpath = self.subpath_for(dst)
        change = self._find_change(subpath)
        if not change and dst[:self.dst_assets_dir_len] == self.dst_assets_dir:
            base = dst[self.dst_assets_dir_len + 1:]
            change = self._find_change(base)
        if not change and dst[:self.dst_blocks_dir_len] == self.dst_blocks_dir:
            base = os.path.basename(dst)
            change = self._find_change(base)
        if not change:
            change = self.default_change
        if not change:
            return
        self.record_change(subpath)
        override = os.path.join(self.override_top, subpath)
        if os.path.isfile(override):
            if change.use_override:
                print '%s: using overridden file: %s' % (
                    change.name(), override)
                src = override
            else:
                print '%s ignored: %s (overridden)' % (change.name(), subpath)
                return
        change.apply(src, dst, subpath)


class ContinuityPass(Pass):
    def __init__(self, ctm_pass):
        super(ContinuityPass, self).__init__(core, continuity)
        self.connectivity_pass = ctm_pass

    def parse_config(self, config):
        for change_name, targets in config.items('changes'):
            change = change_by_name[change_name]
            for target in targets.split():
                self.set_change(os.path.join('assets', 'minecraft', 'textures', 'blocks', target), change)

    def record_change(self, subpath):
        self.connectivity_pass.add_known(subpath)


class ConnectivityPass(Pass):
    def __init__(self):
        super(ConnectivityPass, self).__init__(core, connectivity)
        self.edgeless_top = normpath('continuity')  # use the generated edgless images
        self.edgeless_block_dir = self.src_blocks_dir.replace(core, continuity)
        self.block_subpath = self.dst_blocks_dir[len(self.dst_top) + 1:]

    def parse_config(self, config):
        # noinspection PyAttributeOutsideInit
        self.template_top = os.path.join(self.repack_dir, 'ctm_templates')
        for template_name, targets in config.items('ctm'):
            change = ConnectedTextureChange(template_name, self)
            for target in targets.split():
                self.set_change(target, change)
        if len(self.re_changes) > 0:
            SyntaxError('Cannot use RE\'s in %s (%s)' % (self.repack_dir, self.re_changes))

    def add_known(self, subpath):
        is_block = subpath.startswith(self.block_subpath)
        if is_block and subpath not in self.change_for:
            SyntaxError('No Connectivity spec for %s' % subpath)


for output_dir in (continuity, connectivity):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

connectivity_pass = ConnectivityPass()
passes = (ContinuityPass(connectivity_pass), connectivity_pass)

passes[0].default_change = CopyChange()


# This is copied from shutil, because I need the copy_function option which
# wasn't added until 3.3 or so. Sigh.

# Also added option to overlay on target instead of removing it

# noinspection SpellCheckingInspection
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
        if 'glass' in name:
            print 'copytree %s -> %s' % (srcname, dstname)
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


# noinspection PyUnusedLocal
def only_pack_files(directory, files):
    return [f for f in files if skip_dirs_re.match(f) or do_not_copy_re.search(f)]


# noinspection PyUnusedLocal
def only_png(directory, files):
    return [f for f in files if f[-4:] != '.png']


for p in passes:
    p.run()

if len(warnings):
    print '\n'.join(warnings)
