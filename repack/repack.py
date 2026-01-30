#!/usr/bin/env python3
# coding=utf-8

import configparser
import copy
import errno
import os
import re
import shutil

import javaproperties
from PIL import Image
from PIL import ImageDraw

__author__ = 'arnold'

from PIL.Image import Palette

re_re = re.compile(r'[][?*()\\+|]')
target_opt_re = re.compile(r'([^:@]*):?(.*)')
tile_spec_re = re.compile(r'(\d+)x(\d+)(?:@(\d+),(\d+))?')
block_id_re = re.compile(r'(\d+):?([\d&-]*)')
ctm_opt_re = re.compile(r'^(T:|T$)?([|a-z0-9_]*):?@?([0-9]+)?$')
skip_dirs_re = re.compile(r'^\.|^(no|alternates|parts|variants)$')
solid_prop_re = re.compile(r'\nsolid=(\d+)\n')

# Keep the support file list (.bak, .psd, ...) consistent with report_default.cfg
do_not_copy_re = re.compile(r'\.(ai|bak|cfg|DS_Store|gif|psd|pxd|pyc|py|sh|tiff)$|/(.$|\.)')

warnings = []


def normpath(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


core = normpath('core')
clarity = normpath('clarity')
continuity = normpath('continuity')
connectivity = normpath('connectivity')


class Change(object):
    """
    Base class for a single change operation. Options are specified after a ':', and are interpreted by the specific
    subclass.
    """

    def __init__(self):
        self.use_override = False

    def apply(self, src, dst, subpath):
        print("%s -> %s" % (self.name(), subpath))
        src_img = Image.open(src).convert('RGBA')
        self.do_change(dst, src_img)

    def do_change(self, dst, src_img):
        """Orveride to do the actual work."""
        pass

    def name(self):
        return self.__class__.__name__.replace('Change', '')

    def set_options(self, label, opt_str):
        """Overide to add options for a specific kind of change."""
        if opt_str:
            raise SyntaxError('%s: No options allowed' % self.name())

    def modified(self, label, opt_str):
        m = copy.deepcopy(self)
        m.set_options(label, opt_str)
        return m


class CopyChange(Change):
    """A change that is a simply copy, that is, that actually doesn't change anything."""

    def apply(self, src, dst, subpath):
        if not do_not_copy_re.search(dst):
            shutil.copy2(src, dst)


class SimpleChange(Change):
    """
    Base class for simple changes that only modify the image. This class takes care of reading and writing the
    image, so the sublclass can just do the image work.
    """

    def do_change(self, dst, src_img):
        """
        Creates the destination image and invokes self.simple_change to do the actual work on the image, and then
        saves it under the same name in the destination.. This is good for basic things that only modify the contents
        of the copied image.
        """
        dst_img = Image.new('RGBA', src_img.size)
        self.simple_change(src_img, dst_img)
        save(dst_img, dst)

    def simple_change(self, src_img, dst_img):
        pass


class EraseEdgeChange(SimpleChange):
    """
    A simple change that overwrites the outer border with the pixles that are just inside it.
    """

    def __init__(self, dup_size=None):
        super(SimpleChange, self).__init__()
        self.dup_size = dup_size

    def set_options(self, label, opt_str):
        if len(opt_str):
            self.dup_size = int(opt_str)

    def simple_change(self, src_img, dst_img):
        dst_img.paste(src_img)

        w, h = src_img.size
        anim_count = int(h / w)
        for a in range(0, anim_count):
            b = w - 1  # index of bottom row
            e = w - 1  # index of end column
            copy_start = 0

            dup_size = self.dup_size
            if dup_size is not None:
                copy_start = (w - dup_size) / 2
                copy_width = dup_size
            else:
                copy_start = 1
                copy_width = w - 2

            copy_end = copy_start + copy_width

            def copy_row(row_from, row_to):
                t = src_img.crop((copy_start, row_from, copy_end, row_from + 1))
                if dup_size is None:
                    dst_img.paste(t, (0, row_to))  # set the leftmost pixel
                    dst_img.paste(t, (2, row_to))  # set the rightmost pixel
                dst_img.paste(t, (copy_start, row_to))

            def copy_col(col_from, col_to):
                t = src_img.crop((col_from, y + copy_start, col_from + 1, y + copy_end))
                dst_img.paste(t, (col_to, y + copy_start))

            y = a * w
            copy_row(y + 1, y)  # set the top row from its neighbor
            copy_row(y + b - 1, y + b)  # set the bottom row from its neighbor
            copy_col(1, 0)  # set the left row from its neighbor
            copy_col(e - 1, e)  # set the right row form its neighbor


class TileOverEdge(SimpleChange):
    """
    A simple change that takes a subpart of the image and tiles it over the entire image. The options specify the
    coordinates of the tile and its size.
    """

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
            size = tuple(int((i - 2) / 4) * 4 for i in src_img.size)
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


# The change type based on a name, which is the key in the config, as in:
#     copy: a, b, c
change_by_name = {
    'copy': CopyChange(),
    'erase_edge': EraseEdgeChange(),
    'tile_over_edge': TileOverEdge()}


def to_box(coords):
    """Canonicalize a set of coords to ensure the are upper left corner to lower right."""
    if coords[0] > coords[2]:
        coords[0], coords[2] = coords[2], coords[0]
    if coords[1] > coords[3]:
        coords[1], coords[3] = coords[3], coords[1]
    return coords


def deanimate(img):
    """Reduce an animation to its first frame."""
    if img.size[0] < img.size[1]:
        print('    Taking first frame of animation')
        return img.crop((0, 0, img.size[0], img.size[0]))
    return img


def save(dst_img, dst):
    """Save an image to a file after remove any unused alpha channel."""
    if 'A' in dst_img.getbands():
        alpha = dst_img.split()[-1]
        if all(c == 255 for c in alpha.get_flattened_data()):
            dst_img = dst_img.convert('P', palette=Palette.ADAPTIVE)
    else:
        dst_img = dst_img.convert('P', palette=Palette.ADAPTIVE)
    dst_img.save(dst)


class ConnectedTextureChange(Change):
    """
    A change that builds the connected texture data for the block. This uses a set of named templates, and the config
    file lists which template to use for any given file. Unlisted files are not connected.
    """
    mask_cache = {}

    def __init__(self, template_name, ctm_pass):
        super(Change, self).__init__()
        self.ctm_pass = ctm_pass
        self.template_name = template_name
        self.template_dir = os.path.join(ctm_pass.template_top, template_name)
        self.use_override = True
        self.id_specs = ()
        self.do_tile_source = False
        self.edge_width = 1

    def name(self):
        return 'CTM(%s)' % self.template_name

    def set_options(self, label, opt_str):
        m = ctm_opt_re.match(opt_str or '')
        opts, id_specs, edge_width_spec = m.groups()
        short_label = os.path.basename(label)
        if short_label[:-4] == '.png':
            short_label = short_label[0:-4]
        self.id_specs = (short_label,)
        if len(id_specs):
            self.id_specs += tuple(id_specs.split('|'))
        self.do_tile_source = opts and 'T' in opts
        if edge_width_spec:
            self.edge_width = int(edge_width_spec)

    def apply(self, src, dst, subpath):
        CopyChange().apply(src, dst, subpath)
        super(ConnectedTextureChange, self).apply(src, dst, subpath)

    def do_change(self, dst, src_img):
        ctm_top_dir = os.path.join(self.ctm_pass.dst_assets_dir, 'optifine', 'ctm')
        safe_mkdirs(ctm_top_dir)

        base = os.path.basename(dst)[:-4]
        ctm_dir = os.path.join(ctm_top_dir, base)

        override_path = ctm_dir.replace(self.ctm_pass.dst_top, self.ctm_pass.override_top)
        if os.path.exists(override_path):
            shutil.copytree(override_path, ctm_dir)
            return

        def connected_images(src_path, dst_path):
            self._mask_block(src_path, dst_path, src_img, edgeless_img)

        edgeless_img = self.edgeless_image(base)

        # Someday handle animations in this area
        src_img = deanimate(src_img)
        edgeless_img = deanimate(edgeless_img)

        shutil.copytree(self.template_dir, ctm_dir, ignore=only_png, copy_function=connected_images)

        template_prop_file = os.path.join(self.template_dir, 'block.properties')
        with open(template_prop_file) as t:
            props = javaproperties.load(t)

        # For these blocks, the right default block is the one with solid borders, which matters for getting the item
        # right
        if 'solid' in props:
            solid_src = os.path.join(ctm_dir, '%s.png' % props['solid'])
            shutil.copy(solid_src, dst)

        id_specs = list(self.id_specs)
        id_specs[0] = base
        prop_file = os.path.join(ctm_dir, '%s.properties' % base)
        match = 'matchTiles' if self.do_tile_source else 'matchBlocks'
        props[match] = ' '.join(id_specs)
        with open(prop_file, mode='w') as o:
            javaproperties.dump(props, o, timestamp=None)

    def edgeless_image(self, base):
        edgeless = os.path.join(self.ctm_pass.edgeless_block_dir, base + '.png')
        return Image.open(edgeless).convert('RGBA')

    def modified(self, label, opt_str):
        # Must remove ctm_pass before deep copy or we copy too much -- it is the one thing we don't want to deep copy
        # (looked at overriding __deepcopy__(memo) but it seemed more complicated, not less
        ctm_pass = self.ctm_pass
        self.ctm_pass = None
        m = super(ConnectedTextureChange, self).modified(label, opt_str)
        self.ctm_pass = ctm_pass
        m.ctm_pass = ctm_pass
        return m

    def _mask_block(self, mask, dst, block_img, edgeless_img):
        assert block_img.size == edgeless_img.size

        # block_img.show()
        key = (mask, block_img.size[0], self.edge_width)
        try:
            mask_img, edger = ConnectedTextureChange.mask_cache[key]
        except KeyError:
            mask_img = Image.open(mask).convert('RGBA')
            # mask_img.show()
            mask_img, edger = self.rescale_mask(mask_img, block_img.size)
            ConnectedTextureChange.mask_cache[key] = (mask_img, edger)

        dst_img = edgeless_img.copy()
        dst_img.paste(block_img, mask_img)
        edger(block_img, dst_img)
        save(dst_img, dst)
        return

    def rescale_mask(self, o_mask, img_size):
        assert o_mask.size[0] == o_mask.size[1]
        assert img_size[0] == img_size[1]
        n_mask = o_mask.resize(img_size)
        o_size = o_mask.size[0]
        n_size = img_size[0]
        scale = int(n_size / o_size)

        draw = ImageDraw.Draw(n_mask)

        if scale > 1:
            draw.rectangle((1, 1, n_size - 2, n_size - 2), fill=(0, 0, 0, 0))
            bar = n_mask.crop((scale, 0, 2 * scale - 1, n_size))
            n_mask.paste(bar, (1, 0))
            n_mask.paste(bar, (n_size - scale, 0))
            bar = n_mask.crop((0, scale, n_size, 2 * int(scale) - 1))
            n_mask.paste(bar, (0, 1))
            n_mask.paste(bar, (0, n_size - scale))

        edger = lambda edged_img, block_img: None
        if self.edge_width > 1:
            edger = lambda edged_img, block_img: self.extend_edges(scale, o_mask, edged_img, block_img)

        return n_mask, edger

    def extend_edges(self, scale, o_mask, edged_img, dst_img):
        last = o_mask.size[0] - 1
        for corner in ((0, 0), (0, last), (last, last), (last, 0)):
            self.corner_edge(corner, scale, o_mask, edged_img, dst_img)

    def corner_edge(self, corner, scale, mask, edged_img, dst_img):
        """
        Given a mask, figure out how to handle the edge in the given corner. When the edge width is one, this is trivial
        and so this code is not used (although it should work).

        There are the following possible cases:

        (*) The corner is "on" in the mask and connected along both x and y axes. In this case, the edge on the image is
            already correct, so do nothing.
        (*) The corner is not "on" in the mask. This also means that no line runs to the corner. In this case, fill the
            corner of the image with the nearest color from the center.
        (*) The corner is "on" in the mask, and is connected to along one axis. In this case, smear the end of the edge
            closest along that axis through the corner, extending the edge along that axis out to the edge of the image.
        (*) The corner is "on" in the mask, but no line runs to it. In this case, the corner will be attached to edges
            from adjacent blocks, and the corner "turns the corner" with that edge.

        :param corner: The (x,y) coords of the corner
        :param scale: Scale of the image compared to the mask
        :param mask: The mask
        :param edged_img: The image that contains the edge
        :param dst_img: The final image, which at this stage has been de-edged
        :return: The incoming image, modified
        """

        w = self.edge_width
        # The corner pixel in question (in the edged and block images)
        cx, cy = corner
        # Mask x,y that contains the corner pixel
        mx, my = int(cx / scale), int(cy / scale)

        # The direction away from the pixel towards the middle
        x_dir, y_dir = 1 if cx == 0 else -1, 1 if cy == 0 else -1

        # Offset towards the middle for a full edge_width-sized step
        x_step, y_step = x_dir * w, y_dir * w

        # Is this corner "on" in the mask?
        on = test_is_on(mask, mx, my)
        # Is the pixel next door (on the X axis) "on"?
        on_x = test_is_on(mask, mx + x_dir, my)
        # Is the pixel next door (on the Y axis) "on"?
        on_y = test_is_on(mask, mx, my + y_dir)

        if on_x and on_y:
            # Solid corner, nothing to do
            return

        b_size = dst_img.size[0]

        # In areas with missing lines, smear out the nearest interior bar of the image to the edge
        if not on_x:
            bar = dst_img.crop(to_box([w, cy + y_step, b_size - w, cy + y_step + y_dir]))
            for y in range(0, w * y_dir, y_dir):
                dst_img.paste(bar, (w, cy + y))
        if not on_y:
            bar = dst_img.crop(to_box([cx + x_step, w, cx + x_step + x_dir, b_size - w]))
            for x in range(0, w * x_dir, x_dir):
                dst_img.paste(bar, (cx + x, w))
            if not on:
                # !on implies !on_y and !on_x, so those fills have already happened, now set the corner itself to the
                # center fill color and return.
                assert not on_x
                draw = ImageDraw.Draw(dst_img)
                c = bar.getpixel((0, 0))
                draw.rectangle(to_box([cx, cy, cx + x_step, cy + y_step]), fill=c)
                return

        if not on_x and not on_y:
            # Just the corner (an outside turn)
            assert on
            x_src = [edged_img.getpixel((cx + x, cy + y_step)) for x in range(0, w * x_dir, x_dir)]
            y_src = [edged_img.getpixel((cx + x_step, cy + y)) for y in range(0, w * y_dir, y_dir)]
            for x in range(0, w):
                c = x_src[x]
                for y in range(w - x - 1, w):
                    dst_img.putpixel((cx + x * x_dir, cy + y * y_dir), c)
            for y in range(0, w):
                c = y_src[y]
                for x in range(0, y + 1):
                    dst_img.putpixel((cx + x * x_dir, cy + y * y_dir), c)
        elif on_x:
            # continuous along X, so stretch a Y-oriented bar along X
            box = to_box([cx + x_step, cy, cx + x_step + x_dir, cy + y_step])
            bar = dst_img.crop(box)
            for x in range(0, w * x_dir, x_dir):
                dst_img.paste(bar, (cx + x, box[1]))
        else:
            # continuous along Y, so stretch a X-oriented bar along Y
            assert on_y
            box = to_box([cx, cy + y_step, cx + x_step, cy + y_step + y_dir])
            bar = dst_img.crop(box)
            for y in range(0, w * y_dir, y_dir):
                dst_img.paste(bar, (box[0], cy + y))


def test_is_on(mask, mx, my):
    """Returns true if a pixel is set to 'on' in the mask"""
    return mask.getpixel((mx, my))[3] != 0


def safe_mkdirs(dst_dir):
    try:
        os.makedirs(dst_dir)
    except os.error as e:
        if e.errno != errno.EEXIST:
            raise


def _target_re(target):
    """If the target is an regexp, returns the compiled pattern with a '.png' added, otherwise returns None."""
    # TODO: Is this really needed? A pattern with no special chars still matches what it should.
    if re_re.search(target):
        return re.compile(r'%s\.png' % target)
    return None


class Pass(object):
    """
    A single pass of the repack process. This base class is used for each pack derived from the core.
    """

    def __init__(self, src_name, dst_name):
        self.default_change = CopyChange()
        self.src_top = normpath(src_name)
        self.dst_top = normpath(dst_name)
        self.repack_dir = self.dst_top + '.repack'
        self.override_top = os.path.join(self.repack_dir, 'override')
        self.dst_assets_dir = os.path.join(self.dst_top, 'assets', 'minecraft')
        self.dst_assets_dir_len = len(self.dst_assets_dir)
        self.dst_block_dir = os.path.join(self.dst_assets_dir, 'textures', 'block')
        self.dst_block_dir_len = len(self.dst_block_dir)
        self.src_block_dir = self.dst_block_dir.replace(self.dst_top, self.src_top)
        self.changes_for = {}
        self.re_changes = []

    def parse_config(self, config):
        """
        Parses the 'changes' section in the config file. This reads file as a key, followed by a set of target (path)\
        and option) specifications whose change is defined by that key.
        """
        try:
            for change_name, targets in config.items('changes'):
                change = self.find_change(change_name)
                for target in targets.split():
                    self.set_changes(os.path.join('assets', 'minecraft', 'textures', 'block', target), change)
        except configparser.NoSectionError:
            pass

    def find_change(self, change_name):
        return change_by_name[change_name]

    def record_change(self, subpath):
        pass

    def set_changes(self, target, change):
        """
        Sets the change that will be used for the given target, including handling when the target is a regexp.
        """
        m = target_opt_re.match(target)
        if m:
            target, opt_str = m.groups()
        else:
            target, opt_str = target, ''
        change = change.modified(target, opt_str)
        regexp = _target_re(target)
        if regexp:
            self.re_changes.append((regexp, change))
        else:
            path = target + '.png'
            if path in self.changes_for:
                self.changes_for[path] += (change,)
            else:
                self.changes_for[path] = (change,)

    def _find_changes(self, path_png):
        """
        Find which change(s) to use for the given path.
        """
        if path_png.endswith('.png'):
            path = path_png[:-4]
        else:
            return None

        # look for exact match of name
        k = None
        if path in self.changes_for:
            k = path
        elif path_png in self.changes_for:
            k = path_png
        if k:
            self.unused_changes.remove(k)
            return self.changes_for[k]

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
                return (change,)

        return None

    def run(self):
        """
        Run this pass. This recurisively descends the source resourcepack, deciding what to do with each individual
        entity.  Each iteration in the loop goes through the files in a single directory, deciding what to do with
        each and whether or not to descend into a given subdirectory. For each file in the dir, it execute the
        appropriate changes during the copy.
        """
        print("=== %s" % self.dst_top)

        config = configparser.ConfigParser()
        config.read(os.path.join(self.repack_dir, 'repack.cfg'))
        self.parse_config(config)
        self.unused_changes = set(
            list(self.changes_for.keys()) + [c[0].pattern for c in self.re_changes])

        if os.path.isdir(self.dst_top):
            shutil.rmtree(self.dst_top)
        for dir_name, subdir_list, file_list in os.walk(self.src_top, topdown=True):
            src_dir = dir_name
            dst_dir = dir_name.replace(self.src_top, self.dst_top)
            subdirs_to_skip = [d for d in subdir_list if skip_dirs_re.match(d)]
            for d in subdirs_to_skip:
                subdir_list.remove(d)
            print('-- %s' % (dst_dir))
            safe_mkdirs(dst_dir)
            file_list = [f for f in file_list if not do_not_copy_re.search(f)]
            for f in file_list:
                src = os.path.join(src_dir, f)
                dst = os.path.join(dst_dir, f)
                self.changes(src, dst)
        if len(self.unused_changes):
            global warnings
            warnings += (self.__class__.__name__ + ': Changes not done: Files not found: %s' % ', '.join(
                self.unused_changes),)

    def subpath_for(self, dst):
        dst = normpath(dst)
        subpath = dst[len(self.dst_top) + 1:]
        return dst, subpath

    def changes(self, src, dst):
        """
        Runs the change(s) for a given src and dst file. This is looked up in multiple ways. For a dst of
            'clarity/assets/minecraft/textures/block/lime_stained_glass.png'
        we search the following in order, stopping with the first match
            'assets/minecraft/textures/block/lime_stained_glass.png'
            'textures/block/lime_stained_glass.png'
            'lime_stained_glass.png'
        If nothing is found, we use the default change.

        For input we use the files from the source unless there is a specific override under the 'overrides' directory.
        """
        dst, subpath = self.subpath_for(dst)  # the path from "assests/minecraft" on down.
        changes = self._find_changes(subpath)
        if not changes and dst[:self.dst_assets_dir_len] == self.dst_assets_dir:
            # If the full path for the dst doesn't give us changes, try path from below "assets/minecraft".
            base = dst[self.dst_assets_dir_len + 1:]
            changes = self._find_changes(base)
        if not changes and dst[:self.dst_block_dir_len] == self.dst_block_dir:
            base = os.path.basename(dst)
            changes = self._find_changes(base)
        if not changes:
            changes = (self.default_change,)

        self.record_change(subpath)
        override = os.path.join(self.override_top, subpath)

        # Apply all the changes
        for change in changes:
            if os.path.isfile(override):
                if change.use_override:
                    print('%s: using overridden file: %s' % (
                        change.name(), override))
                    src = override
                else:
                    shutil.copy(override, dst)
                    print('%s: %s overridden' % (change.name(), subpath))
                    return
            change.apply(src, dst, subpath)


class ContinuityPass(Pass):
    """
    The pass for the Continuity pack. This remembers the CTM pass so it can tell it about files it processes, which
    sets up the CTM pass for its work.
    """

    def __init__(self, ctm_pass):
        super(ContinuityPass, self).__init__(core, continuity)
        self.connectivity_pass = ctm_pass


class ConnectivityPass(Pass):
    """
    The pass for the Connectivity (CTM) pass. Each connectivity texture requires both edged and edgeless blocks. The
    edgless blocks are taken from the previously-generated Continuity pack.
    """

    def __init__(self):
        super(ConnectivityPass, self).__init__(core, connectivity)
        self.edgeless_top = normpath('continuity')  # use the generated edgeless images
        self.edgeless_block_dir = self.src_block_dir.replace(core, continuity)
        self.block_subpath = self.dst_block_dir[len(self.dst_top) + 1:]
        self.template_top = os.path.join(self.repack_dir, 'ctm_templates')

    def find_change(self, change_name):
        return ConnectedTextureChange(change_name, self)


def only_png(_, files):
    return [f for f in files if f[-4:] != '.png']


# Build the pass objects.
clarity_pass = Pass(core, clarity)
continuity_pass = Pass(core, continuity)
connectivity_pass = ConnectivityPass()
passes = (clarity_pass, continuity_pass, connectivity_pass)

passes[0].default_change = CopyChange()

for p in passes:
    p.run()

if len(warnings):
    print('\n'.join(warnings))
