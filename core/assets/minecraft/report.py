#!/usr/bin/env python
import os
import re
import subprocess
import ConfigParser
import sys

import Image
import ImageChops

__author__ = 'arnold'

status_by_name = {}


def no_path(groups):
    return None


def whole_match(groups):
    assert len(groups) == 1
    return groups[0]


def first_group(groups):
    assert len(groups) == 2
    return groups[1]


def path_from_only(groups):
    path = None
    assert len(groups) == 2
    if len(groups[0]) > 0:
        path = os.path.join(groups[0], groups[1])
    else:
        path = groups[1]
    return path


class FileStatus(object):
    def __init__(self, prefix, pattern, ignore_pats=(), path_from_groups=whole_match):
        self.pat = re.compile(pattern)
        self.prefix = prefix
        self.files = set()
        self.ignore = []
        self.path_from_groups = path_from_groups
        try:
            to_ignore = config.get('ignore', prefix.lower())
            all_ignored = ignore_pats + tuple(to_ignore.split())
            self.ignore = [re.compile(pat) for pat in all_ignored]
        except ConfigParser.NoOptionError:
            pass
        status_by_name[self.prefix] = self

    def status_match(self, line):
        m = self.pat.search(line)
        if m:
            groups = m.groups()
            path = self.path_from_groups(groups) if len(groups) else None
            if path and not any(pat.search(path) for pat in self.ignore):
                self.add_path(groups, path)
        return m

    def dump(self):
        for f in sorted(self.files):
            print '%s: %s' % (self.prefix, f)

    def add_path(self, groups, path):
        self.files.add(path)


# This does an extra check for changed PNG files to see if they are really different
class ChangedFileStatus(FileStatus):
    def __init__(self, prefix, pattern, same_file_status, ignore_pats=()):
        super(ChangedFileStatus, self).__init__(prefix, pattern, ignore_pats, first_group)
        self.same_file_status = same_file_status

    def add_path(self, groups, path):
        if path.endswith('.png'):
            # Check if they are equivalent images, just encoded differently.
            img1 = Image.open(groups[0])
            img2 = Image.open(groups[1])
            if img1.size == img2.size and ImageChops.difference(img1.convert('RGBA'),
                                                                img2.convert('RGBA')).getbbox() is None:
                self.same_file_status.add_path(groups, path)
                return
        self.files.add(path)


config_file = 'report_default.cfg'
if len(sys.argv) > 1:
    config_file = sys.argv[1]

config = ConfigParser.SafeConfigParser()
config.read(config_file)

other = config.get('basic', 'top')
other_esc = other.replace('.', '\\.')

always_added = ('.gitignore', 'font/alternate.properties',
                'font/default.properties', 'textures/gui/container/parts',
                r'_colored\.png$', r'\.pxm$', r'\.py$', r'.sh$', r'\.tiff$',
                r'\.cfg$', r'(^|/).$', r'(^|/)\..$')

same_checker = FileStatus('Same', r'^Files (?:\./)?(.*) and ', path_from_groups=no_path)
statuses = (
    FileStatus('Ignored', r'\.swp|\~|\/.$|\.DS_Store', path_from_groups=whole_match),
    same_checker,
    ChangedFileStatus('Changed', r'^Binary files (?:\./)?(.*) and ([^\s]*)', same_checker),
    FileStatus('Missing', r'^Only in ' + other_esc + '/?(.*): (.*)', path_from_groups=path_from_only),
    FileStatus('Added', r'^Only in \./?(.*): (.*)', always_added, path_from_groups=path_from_only)
)

diff = subprocess.Popen(['diff', '-rs', '.', other], stdout=subprocess.PIPE)

for line in diff.stdout:
    for status in statuses:
        if status.status_match(line):
            break

print_order = ['Missing', 'Added', 'Same', 'Changed']

for name in print_order:
    status = status_by_name[name]
    status.dump()
