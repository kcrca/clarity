import ConfigParser
import os
import re
import shutil
import sys
import Image

__author__ = 'arnold'

re_pat = re.compile(r'[][?*()\\+|]')
block_id_pat = re.compile(r'(\d+):?(\d*)')


class Transform(object):
    def transform(self, src, dst, subpath):
        print "%s -> %s" % (self.name(), subpath)
        src_img = Image.open(src).convert('RGBA')
        self.do_transform(dst, src_img)

    def do_transform(self, dst, src_img):
        pass

    def name(self):
        pass


class CopyTransform(Transform):
    def transform(self, src, dst, subpath):
        shutil.copy2(src, dst)

    def name(self):
        return 'Copy'


class SimpleTransform(Transform):
    def do_transform(self, dst, src_img):
        dst_img = Image.new('RGBA', src_img.size)
        self.simple_transform(src_img, dst_img)
        dst_img.save(dst)

    def simple_transform(self, src_img, dst_img):
        pass


class MaskTransform(SimpleTransform):
    def __init__(self, mask_name):
        super(MaskTransform, self).__init__()
        self.mask_name = mask_name
        mask_file = os.path.join(config_dir, 'masks', '%s.png' % mask_name)
        self.img = Image.open(mask_file)

    def name(self):
        return 'Mask %s' % self.mask_name

    def simple_transform(self, src_img, dst_img):
        dst_img.paste(src_img, self.img)


class EraseEdgeTransform(SimpleTransform):
    def name(self):
        return 'Erase Edge'

    def simple_transform(self, src_img, dst_img):
        dst_img.paste(src_img)

        w, h = src_img.size
        b = h - 1 # index of bottom row
        e = w - 1 # index of end column

        # set the top row from its neighbor
        t = src_img.crop((1, 1, e, 2))
        dst_img.paste(t, (0, 0)) # set the upper left pixel
        dst_img.paste(t, (2, 0)) # set the upper right pixel
        dst_img.paste(t, (1, 0))

        # set the bottom row from its neighbor
        t = src_img.crop((1, b - 1, e, b))
        dst_img.paste(t, (0, b)) # set the lower left pixel
        dst_img.paste(t, (2, b)) # set the lower right pixel
        dst_img.paste(t, (1, b))

        # set the left row from its neighbor
        t = src_img.crop((1, 1, 2, b))
        dst_img.paste(t, (0, 1))

        # set the right row form its neighbor
        t = src_img.crop((e - 1, 1, e, b))
        dst_img.paste(t, (e, 1))


class TileOverEdge(SimpleTransform):
    def name(self):
        return 'Tile over edge'

    def simple_transform(self, src_img, dst_img):
        w, h = src_img.size
        b = h - 1 # index of bottom row
        e = w - 1 # index of end column

        t = src_img.crop((1, 1, e, b))
        dst_img.paste(t, (0, 0))
        t = src_img.crop((3, 1, 5, b))
        dst_img.paste(t, (e - 1, 0))
        t = dst_img.crop((0, 2, w, 4))
        dst_img.paste(t, (0, b - 1))


class ContinuousTransform(Transform):
    def __init__(self, template_name):
        super(Transform, self)
        self.template_name = template_name
        self.template_dir = '%s/ctm_templates/%s' % (config_dir, template_name)


    def name(self):
        return 'CTM(%s)' % self.template_name

    def do_transform(self, dst, src_img):
        ctm_top_dir = os.path.join(inner_top, 'mcpatcher', 'ctm')
        if not os.path.isdir(ctm_top_dir):
            os.makedirs(ctm_top_dir)

        base = os.path.basename(dst)[:-4]
        block_id_str = config.get('ids', base)
        block_id, block_dmg = block_id_pat.match(block_id_str).groups()
        ctm_dir = os.path.join(ctm_top_dir, base)

        edgeless_img = Image.new('RGBA', src_img.size)
        EraseEdgeTransform().simple_transform(src_img, edgeless_img)

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
        self.xform_for = {}
        self.re_xforms = []
        self.default_xform = None

    def set_xform(self, target, xform):
        re = self._target_re(target)
        if re:
            self.re_xforms.append((re, xform))
        else:
            path = target + '.png'
            if path in self.xform_for:
                existing = self.xform_for[target]
                print 'Duplicate transform for %s: %s and %s' % (
                    target, xform.name(), existing.name())
            else:
                self.xform_for[path] = xform

    def _find_xform(self, path):
        path_png = path + '.png'

        # look for exact match of name
        k = None
        if path in self.xform_for:
            k = path
        elif path_png in self.xform_for:
            k = path_png
        if k:
            self.unused_xforms.remove(k)
            return self.xform_for[k]

        # look for pattern match
        for (re, xform) in self.re_xforms:
            k = None
            if re.search(path):
                k = path
            elif re.search(path_png):
                k = path_png
            if k:
                try:
                    self.unused_xforms.remove(re.pattern)
                except KeyError:
                    pass
                return xform

        return None

    def run(self):
        self.unused_xforms = set(
            self.xform_for.keys() + [p[0].pattern for p in self.re_xforms])
        copytree(src_dir, dst_dir, ignore=ignore_dots,
                 copy_function=self.transform,
                 overlay=True)
        if len(self.unused_xforms):
            print 'Transforms not done: Files not found: %s' % ', '.join(
                self.unused_xforms)


    def transform(self, src, dst):
        dst, subpath = subpath_for(dst)
        xform = self._find_xform(subpath)
        if not xform and dst[:inner_top_len] == inner_top:
            base = dst[inner_top_len + 1:]
            xform = self._find_xform(base)
        if not xform and dst[:texture_dir_len] == texture_dir:
            base = os.path.basename(dst)
            xform = self._find_xform(base)
        if not xform:
            xform = self.default_xform
        if not xform:
            return
        overrides_path = os.path.join(overrides_dir, subpath)
        if os.path.isfile(overrides_path):
            print '%s ignored: %s (overridden)' % (xform.name(), subpath)
            return
        xform.transform(src, dst, subpath)

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

passes[0].default_xform = CopyTransform()

try:
    for mask_name, targets in config.items('masks'):
        xform = MaskTransform(mask_name)
        for target in targets.split():
            passes[0].set_xform(target, xform)
except ConfigParser.NoSectionError:
    pass

try:
    xform_by_name = {
        'erase_edge': EraseEdgeTransform(),
        'tile_over_edge': TileOverEdge()}

    for xform_name, targets in config.items('changes'):
        xform = xform_by_name[xform_name]
        for target in targets.split():
            passes[0].set_xform(target, xform)
except ConfigParser.NoSectionError:
    pass

try:
    for template_name, targets in config.items('ctm'):
        xform = ContinuousTransform(template_name)
        for target in targets.split():
            passes[1].set_xform(target, xform)
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

