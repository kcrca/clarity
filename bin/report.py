#!/usr/bin/env python

# Generates a report comparing two packs.

import os
import re
import subprocess
import ConfigParser
import sys

from PIL import Image
from PIL import ImageChops
from clip import *

__author__ = 'arnold'

status_by_name = {}


def no_path(groups):
    return None


def whole_match(groups):
    assert len(groups) == 1
    return groups[0]


def first_group(groups):
    assert len(groups) == 2
    return groups[0]


def path_from_only(groups):
    path = None
    assert len(groups) == 2
    if len(groups[0]) > 0:
        path = os.path.join(groups[0], groups[1])
    else:
        path = groups[1]
    return path


class FileStatus(object):
    def __init__(self, prefix, pattern, path_from_groups=whole_match):
        self.pat = re.compile(pattern)
        self.prefix = prefix
        self.files = set()
        self.ignore = []
        self.unused_ignores = set()
        self.path_from_groups = path_from_groups
        self.multi_matches = dict()
        try:
            to_ignore = config.get('ignore', prefix.lower())
            pats = set(to_ignore.split())
            self.ignore = [re.compile(pat) for pat in pats]
            self.unused_ignores |= pats
        except ConfigParser.NoOptionError:
            pass
        status_by_name[self.prefix] = self

    def status_match(self, line):
        m = self.pat.search(line)
        if m:
            groups = m.groups()
            path = self.path_from_groups(groups) if len(groups) else None
            self.add_path(groups, path)
        return m

    def dump(self):
        for f in sorted(self.files):
            print '%s: %s' % (self.prefix, f)
        if len(self.unused_ignores) > 0:
            print '  UNUSED pattern:', ', '.join(sorted(self.unused_ignores))
        if len(self.multi_matches) > 0:
            print '  MULTIPLE pattern matches for path:'
            for p in sorted(self.multi_matches):
                print '    %s: %s' % (p, ', '.join(self.multi_matches[p]))

    def add_path(self, groups, path):
        """
        Add the given path to list of matches for this path UNLESS it matches the patterns to be ignored.
        """
        if path:
            patterns = []
            for pat in self.ignore:
                if pat.search(path):
                    patterns.append(pat.pattern)
                    self.unused_ignores.discard(pat.pattern)
            if len(patterns) == 0:
                self.files.add(path)
            elif len(patterns) > 1:
                self.multi_matches[path] = patterns


            # This does an extra check for changed PNG files to see if they are really different


class ChangedFileStatus(FileStatus):
    def __init__(self, prefix, pattern, same_file_status, ignore_pats=()):
        super(ChangedFileStatus, self).__init__(prefix, pattern, first_group)
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
        super(ChangedFileStatus, self).add_path(groups, path)


config_file = directory('config', 'report_default.cfg')
if len(sys.argv) > 1:
    config_file = sys.argv[1]

config = ConfigParser.SafeConfigParser()
config.read(config_file)

other = config.get('basic', 'top')
other_esc = other.replace('.', '\\.')

same_checker = FileStatus('Same', r'^Files (?:\./)?(.*) and .* identical', path_from_groups=no_path)
statuses = (
    FileStatus('Ignored', r'\.swp|\~|\/.$|\.DS_Store|_diff\.gif$', path_from_groups=whole_match),
    same_checker,
    ChangedFileStatus('Changed', r'^Files (?:\./)?(.*) and ([^\s]*) differ', same_checker),
    FileStatus('Missing', r'^Only in ' + other_esc + '/?(.*): (.*)', path_from_groups=path_from_only),
    FileStatus('Added', r'^Only in \./?(.*): (.*)', path_from_groups=path_from_only)
)

diff = subprocess.Popen(['diff', '-rsq', '.', other], stdout=subprocess.PIPE)

irrelevant_re = re.compile(r'^[0-9<>-]')

for line in diff.stdout:
    if not irrelevant_re.search(line):
        for status in statuses:
            if status.status_match(line):
                break

print_order = ['Missing', 'Added', 'Same', 'Changed']

for name in print_order:
    status = status_by_name[name]
    status.dump()