import ConfigParser
import os
import shutil
import sys
import Image

__author__ = 'arnold'


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


config = ConfigParser.SafeConfigParser()

src_dir, dst_dir, config_dir = sys.argv[1:]
src_dir = normpath(src_dir)
dst_dir = normpath(dst_dir)

config.read('%s/clarify.cfg' % config_dir)

if os.path.isdir(dst_dir):
    shutil.rmtree(dst_dir)

masks = config.items('masks')
masks_for = {}

for mask_name, mask_targets in masks:
    mask_file = '%s/masks/%s.png' % (config_dir, mask_name)
    img = Image.open(mask_file)
    for target in mask_targets.split():
        masks_for[target + '.png'] = mask_name, img

unused_masks = set(masks_for.keys())

texture_dir = normpath('%s/assets/minecraft/textures/blocks/' % dst_dir)
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
                copytree(srcname, dstname, symlinks, ignore, copy_function, overlay)
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


def mask_for(path):
    k = None
    if path in masks_for:
        k = path
    elif path + '.png' in masks_for:
        k = path + '.png'
    if k:
        unused_masks.remove(k)
        return masks_for[k]
    return None, None


def subpath_for(dst):
    dst = normpath(dst)
    subpath = dst[len(dst_dir) + 1:]
    return dst, subpath


def clarify(src, dst):
    dst, subpath = subpath_for(dst)
    mask_name, mask = mask_for(subpath)
    if not mask and dst[:texture_dir_len] == texture_dir:
        base = os.path.basename(dst)
        mask_name, mask = mask_for(base)
    overrides_path = '%s/%s' % (overrides_dir, subpath)
    if not mask:
        shutil.copy2(src, dst)
        return
    if os.path.isfile(overrides_path):
        print 'mask ignored: %s (overridden)' % subpath
        return
    print "mask: %s -> %s" % (mask_name, subpath)
    src_img = Image.open(src).convert('RGBA')
    dst_img = Image.new('RGBA', src_img.size)
    dst_img.paste(src_img, mask)
    dst_img.save(dst)


def ignore_dots(directory, files):
    return [f for f in files if f[0] == '.']


def verbose_copy(src, dst):
    dst, subpath = subpath_for(dst)
    if os.path.isfile(src):
        action = "overriding" if os.path.exists(dst) else "adding"
        print "%s: %s" % (action, subpath)
    shutil.copy2(src, dst)


copytree(src_dir, dst_dir, ignore=ignore_dots, copy_function=clarify)
copytree(overrides_dir, dst_dir, ignore=ignore_dots, copy_function=verbose_copy, overlay=True)

if len(unused_masks):
    print 'Not found to mask: %s' % (', '.join(unused_masks))
