import ConfigParser
import os
import shutil
import sys
import Image

__author__ = 'arnold'


class Transform(object):
    def act(self, src, dst, subpath):
        print "%s -> %s" % (self.name(), subpath)
        src_img = Image.open(src).convert('RGBA')
        dst_img = Image.new('RGBA', src_img.size)
        self.xform(src_img, dst_img)
        dst_img.save(dst)

    def name(self):
        pass

    def xform(self, src_img, dst_img):
        pass


class MaskTransform(Transform):
    def __init__(self, mask_name):
        super(MaskTransform, self).__init__()
        self.mask_name = mask_name
        mask_file = '%s/masks/%s.png' % (config_dir, mask_name)
        self.img = Image.open(mask_file)

    def xform(self, src_img, dst_img):
        dst_img.paste(src_img, self.img)

    def name(self):
        return 'Mask %s' % mask_name


class NoEdgeTransform(Transform):
    def xform(self, src_img, dst_img):
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

    def name(self):
        return 'No Edge'


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


config = ConfigParser.SafeConfigParser()

src_dir, dst_dir, config_dir = sys.argv[1:]
src_dir = normpath(src_dir)
dst_dir = normpath(dst_dir)

config.read(os.path.join(config_dir, 'repack.cfg'))

if os.path.isdir(dst_dir):
    shutil.rmtree(dst_dir)


def set_xform(target, xform):
    path = target + '.png'
    if path in xform_for:
        existing = xform_for[target]
        print 'Duplicate transform for %s: %s and %s' % (
            target, xform.name(), existing.name())
    else:
        xform_for[path] = xform


xform_for = {}

try:
    for mask_name, targets in config.items('masks'):
        xform = MaskTransform(mask_name)
        for target in targets.split():
            set_xform(target, xform)
except ConfigParser.NoSectionError:
    pass

xform_by_name = {}
xform_by_name['no_edge'] = NoEdgeTransform()

try:
    for xform_name, targets in config.items('changes'):
        xform = xform_by_name[xform_name]
        for target in targets.split():
            set_xform(target, xform)
except ConfigParser.NoSectionError:
    pass

unused_xforms = set(xform_for.keys())

inner_top = normpath('%s/assets/minecraft' % dst_dir)
inner_top_len = len(inner_top)
texture_dir = normpath('%s/textures/blocks/' % inner_top)
texture_dir_len = len(texture_dir)
overrides_dir = normpath('%s/override' % config_dir)


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


def find_xform(path):
    k = None
    if path in xform_for:
        k = path
    elif path + '.png' in xform_for:
        k = path + '.png'
    if k:
        unused_xforms.remove(k)
        return xform_for[k]
    return None


def subpath_for(dst):
    dst = normpath(dst)
    subpath = dst[len(dst_dir) + 1:]
    return dst, subpath


def mask(src, dst):
    dst, subpath = subpath_for(dst)
    xform = find_xform(subpath)
    if not xform and dst[:inner_top_len] == inner_top:
        base = dst[inner_top_len + 1:]
        xform = find_xform(base)
    if not xform and dst[:texture_dir_len] == texture_dir:
        base = os.path.basename(dst)
        xform = find_xform(base)
    if not xform:
        shutil.copy2(src, dst)
        return
    overrides_path = os.path.join(overrides_dir, subpath)
    if os.path.isfile(overrides_path):
        print '%s ignored: %s (overridden)' % (xform.name(), subpath)
        return
    xform.act(src, dst, subpath)


def ignore_dots(directory, files):
    return [f for f in files if f[0] == '.']


def verbose_copy(src, dst):
    dst, subpath = subpath_for(dst)
    if os.path.isfile(src):
        action = "overriding" if os.path.exists(dst) else "adding"
        print "%s: %s" % (action, subpath)
    shutil.copy2(src, dst)


copytree(src_dir, dst_dir, ignore=ignore_dots, copy_function=mask)
if os.path.exists(overrides_dir):
    copytree(overrides_dir, dst_dir, ignore=ignore_dots,
             copy_function=verbose_copy,
             overlay=True)

if len(unused_xforms):
    print 'Transforms not done: Files not found: %s' % ', '.join(unused_xforms)
