#!/usr/bin/env python
import re
import subprocess
import ConfigParser
import sys

__author__ = 'arnold'

status_by_name = {}


class FileStatus(object):
    def __init__(self, prefix, pattern, ignore_pats=()):
        self.pat = re.compile(pattern)
        self.prefix = prefix
        self.files = set()
        self.ignore = []
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
            path = None
            if len(groups) == 1:
                path = groups[0]
            elif len(groups) == 2:
                if len(groups[0]) > 0:
                    path = groups[0] + '/' + groups[1]
                else:
                    path = groups[1]
            if path and not any(pat.match(path) for pat in self.ignore):
                self.files.add(path)
        return m

    def dump(self):
        for f in sorted(self.files):
            print '%s: %s' % (self.prefix, f)


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

statuses = [
    FileStatus('Ignored', r'\.swp|\~|\/.$|\.DS_Store'),
    FileStatus('Changed', r'^Binary files (?:\./)?(.*) and '),
    FileStatus('Same', r'^Files (?:\./)?(.*) and '),
    FileStatus('Missing', r'^Only in ' + other_esc + '/?(.*): (.*)'),
    FileStatus('Added', r'^Only in \./?(.*): (.*)', always_added)
]

diff = subprocess.Popen(['diff', '-rs', '.', other], stdout=subprocess.PIPE)

for line in diff.stdout:
    for status in statuses:
        if status.status_match(line):
            break

print_order = ['Missing', 'Added', 'Same', 'Changed']

for name in print_order:
    status = status_by_name[name]
    status.dump()
