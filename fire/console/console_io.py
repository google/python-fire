# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""General console printing utilities used by the Cloud SDK."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import signal
import subprocess
import sys

from fire.console import console_attr
from fire.console import console_pager
from fire.console import encoding
from fire.console import files


def IsInteractive(output=False, error=False, heuristic=False):
  """Determines if the current terminal session is interactive.

  sys.stdin must be a terminal input stream.

  Args:
    output: If True then sys.stdout must also be a terminal output stream.
    error: If True then sys.stderr must also be a terminal output stream.
    heuristic: If True then we also do some additional heuristics to check if
               we are in an interactive context. Checking home path for example.

  Returns:
    True if the current terminal session is interactive.
  """
  if not sys.stdin.isatty():
    return False
  if output and not sys.stdout.isatty():
    return False
  if error and not sys.stderr.isatty():
    return False

  if heuristic:
    # Check the home path. Most startup scripts for example are executed by
    # users that don't have a home path set. Home is OS dependent though, so
    # check everything.
    # *NIX OS usually sets the HOME env variable. It is usually '/home/user',
    # but can also be '/root'. If it's just '/' we are most likely in an init
    # script.
    # Windows usually sets HOMEDRIVE and HOMEPATH. If they don't exist we are
    # probably being run from a task scheduler context. HOMEPATH can be '\'
    # when a user has a network mapped home directory.
    # Cygwin has it all! Both Windows and Linux. Checking both is perfect.
    home = os.getenv('HOME')
    homepath = os.getenv('HOMEPATH')
    if not homepath and (not home or home == '/'):
      return False
  return True


def More(contents, out, prompt=None, check_pager=True):
  """Run a user specified pager or fall back to the internal pager.

  Args:
    contents: The entire contents of the text lines to page.
    out: The output stream.
    prompt: The page break prompt.
    check_pager: Checks the PAGER env var and uses it if True.
  """
  if not IsInteractive(output=True):
    out.write(contents)
    return
  if check_pager:
    pager = encoding.GetEncodedValue(os.environ, 'PAGER', None)
    if pager == '-':
      # Use the fallback Pager.
      pager = None
    elif not pager:
      # Search for a pager that handles ANSI escapes.
      for command in ('less', 'pager'):
        if files.FindExecutableOnPath(command):
          pager = command
          break
    if pager:
      # If the pager is less(1) then instruct it to display raw ANSI escape
      # sequences to enable colors and font embellishments.
      less_orig = encoding.GetEncodedValue(os.environ, 'LESS', None)
      less = '-R' + (less_orig or '')
      encoding.SetEncodedValue(os.environ, 'LESS', less)
      # Ignore SIGINT while the pager is running.
      # We don't want to terminate the parent while the child is still alive.
      signal.signal(signal.SIGINT, signal.SIG_IGN)
      p = subprocess.Popen(pager, stdin=subprocess.PIPE, shell=True)
      enc = console_attr.GetConsoleAttr().GetEncoding()
      p.communicate(input=contents.encode(enc))
      p.wait()
      # Start using default signal handling for SIGINT again.
      signal.signal(signal.SIGINT, signal.SIG_DFL)
      if less_orig is None:
        encoding.SetEncodedValue(os.environ, 'LESS', None)
      return
  # Fall back to the internal pager.
  console_pager.Pager(contents, out, prompt).Run()
