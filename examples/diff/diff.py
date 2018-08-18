# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""A command line tool for diffing files.

The Python 2.7 documentation demonstrates how to make a command line interface
for the difflib library using optparse:
https://docs.python.org/2/library/difflib.html#a-command-line-interface-to-difflib

This file demonstrates how to create a command line interface providing the same
functionality using Python Fire.

Usage:

diff FROMFILE TOFILE COMMAND [LINES]

Arguments can be passed positionally or via the Flag syntax.
Using positional arguments, the usage is:

diff FROMFILE TOFILE
diff FROMFILE TOFILE context-diff [LINES]
diff FROMFILE TOFILE unified-diff [LINES]
diff FROMFILE TOFILE ndiff
diff FROMFILE TOFILE make-file [CONTEXT] [LINES]

Using the Flag syntax, the usage is:

diff --fromfile=FROMFILE --tofile=TOFILE
diff --fromfile=FROMFILE --tofile=TOFILE context-diff [--lines=LINES]
diff --fromfile=FROMFILE --tofile=TOFILE unified-diff [--lines=LINES]
diff --fromfile=FROMFILE --tofile=TOFILE ndiff
diff --fromfile=FROMFILE --tofile=TOFILE make-file \
    [--context=CONTEXT] [--lines LINES]

As with any Fire CLI, you can append '--' followed by any Flags to any command.

The Flags available for all Fire CLIs are:
  --help
  --interactive
  --trace
  --separator=SEPARATOR
  --completion
  --verbose
"""

import difflib
import os
import time

import fire


class DiffLibWrapper(object):
  """Provides a simple interface to the difflib module.

  The purpose of this simple interface is to offer a limited subset of the
  difflib functionality as a command line interface.
  """

  def __init__(self, fromfile, tofile):
    self._fromfile = fromfile
    self._tofile = tofile

    self.fromdate = time.ctime(os.stat(fromfile).st_mtime)
    self.todate = time.ctime(os.stat(tofile).st_mtime)
    with open(fromfile) as f:
      self.fromlines = f.readlines()
    with open(tofile) as f:
      self.tolines = f.readlines()

  def unified_diff(self, lines=3):
    return difflib.unified_diff(
        self.fromlines, self.tolines, self._fromfile,
        self._tofile, self.fromdate, self.todate, n=lines)

  def ndiff(self):
    return difflib.ndiff(self.fromlines, self.tolines)

  def make_file(self, context=False, lines=3):
    return difflib.HtmlDiff().make_file(
        self.fromlines, self.tolines, self._fromfile, self._tofile,
        context=context, numlines=lines)

  def context_diff(self, lines=3):
    return difflib.context_diff(
        self.fromlines, self.tolines, self._fromfile,
        self._tofile, self.fromdate, self.todate, n=lines)


def main():
  fire.Fire(DiffLibWrapper, name='diff')

if __name__ == '__main__':
  main()
