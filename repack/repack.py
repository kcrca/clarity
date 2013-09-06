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

warnings = []


class Change(object):
    def change(self, src, dst, subpath):
        print "%s -> %s" % (self.name(), subpath)
        src_img = Image.open(src).convert('RGBA')
        self.do_change(dst, src_img)

    def set_options(self, opt_str):
        raise SyntaxError('%s:No options supported', self.__class__)

    def do_change(self, dst, src_img):
        pass

    def name(self):
        pass

    def set_opt(self, opt_str):
        raise SyntaxError('%s: No options allowed' % self.__class__)

    def modified(self, opt_str):
        m = copy.deepcopy(self)
        m.set_opt(opt_str)
        return m


class CopyChange(Change):
    def change(self, src, dst, subpath):
        shutil.copy2(src, dst)

    def name(self):
        return 'Copy'


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

    def name(self):
        return 'Erase Edge'

    def set_options(self, opt_str):
        if len(opt_str):
            self.dup_size = int(opt_str)

    def simple_change(self, src_img, dst_img):
        dst_img.paste(src_img)

        w, h = src_img.size
        b = h - 1 # index of bottom row
        e = w - 1 # index of end column
        copy_start = 0
        copy_width = src_img.size[0]

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

    def name(self):
        return 'Tile over edge'

    def set_opt(self, opt_str):
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


class ContinuousChange(Change):
    def __init__(self, template_name):
        super(Change, self)
        self.template_name = template_name
        self.template_dir = '%s/ctm_templates/%s' % (config_dir, template_name)
        self.dup_size = None

    def name(self):
        return 'CTM(%s)' % self.template_name

    def set_opt(self, opt_str):
        if len(opt_str):
            self.dup_size = int(opt_str)

    def do_change(self, dst, src_img):
        ctm_top_dir = os.path.join(inner_top, 'mcpatcher', 'ctm')
        if not os.path.isdir(ctm_top_dir):
            os.makedirs(ctm_top_dir)

        base = os.path.basename(dst)[:-4]
        block_id_str = config.get('ids', base)
        block_id, block_dmg = block_id_pat.match(block_id_str).groups()
        ctm_dir = os.path.join(ctm_top_dir, base)

        edgeless_img = Image.new('RGBA', src_img.size)
        EraseEdgeChange(self.dup_size).simple_change(src_img,
                                                     edgeless_img)

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
        copytree(src_dir, dst_dir, ignore=ignore_dots,
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
        overrides_path = os.path.join(overrides_dir, subpath)
        if os.path.isfile(overrides_path):
            print '%s ignored: %s (overridden)' % (change.name(), subpath)
            return
        change.change(src, dst, subpath)

    def _target_re(self, target):
        if re_pat.search(target):
            return re.compile(target + '.png')
        return None


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


config = ConfigParser.SafeConfigParser()

src_dir, dst_dir, config_dir = sys.argv[1:]
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
    change_by_name = {
        'erase_edge': EraseEdgeChange(),
        'tile_over_edge': TileOverEdge()}

    for change_name, targets in config.items('changes'):
        change = change_by_name[change_name]
        for target in targets.split():
            passes[0].set_change(target, change)
except ConfigParser.NoSectionError:
    pass

try:
    for template_name, targets in config.items('ctm'):
        change = ContinuousChange(template_name)
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


def ignore_dots(directory, files):
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
    copytree(overrides_dir, dst_dir, ignore=ignore_dots,
             copy_function=verbose_copy,
             overlay=True)

print '\n'.join(warnings)
