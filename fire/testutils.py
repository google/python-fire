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

# Lint as: python2, python3
"""Utilities for Python Fire's tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
import os
import re
import sys
import unittest

from fire import core
from fire import trace

import mock
import six


class BaseTestCase(unittest.TestCase):
  """Shared test case for Python Fire tests."""

  @contextlib.contextmanager
  def assertOutputMatches(self, stdout='.*', stderr='.*', capture=True):
    """Asserts that the context generates stdout and stderr matching regexps.

    Note: If wrapped code raises an exception, stdout and stderr will not be
      checked.

    Args:
      stdout: (str) regexp to match against stdout (None will check no stdout)
      stderr: (str) regexp to match against stderr (None will check no stderr)
      capture: (bool, default True) do not bubble up stdout or stderr

    Yields:
      Yields to the wrapped context.
    """
    stdout_fp = six.StringIO()
    stderr_fp = six.StringIO()
    try:
      with mock.patch.object(sys, 'stdout', stdout_fp):
        with mock.patch.object(sys, 'stderr', stderr_fp):
          yield
    finally:
      if not capture:
        sys.stdout.write(stdout_fp.getvalue())
        sys.stderr.write(stderr_fp.getvalue())

    for name, regexp, fp in [('stdout', stdout, stdout_fp),
                             ('stderr', stderr, stderr_fp)]:
      value = fp.getvalue()
      if regexp is None:
        if value:
          raise AssertionError('%s: Expected no output. Got: %r' %
                               (name, value))
      else:
        if not re.search(regexp, value, re.DOTALL | re.MULTILINE):
          raise AssertionError('%s: Expected %r to match %r' %
                               (name, value, regexp))

  def assertRaisesRegex(self, *args, **kwargs):  # pylint: disable=arguments-differ
    if sys.version_info.major == 2:
      return super(BaseTestCase, self).assertRaisesRegexp(*args, **kwargs)  # pylint: disable=deprecated-method
    else:
      return super(BaseTestCase, self).assertRaisesRegex(*args, **kwargs)  # pylint: disable=no-member

  @contextlib.contextmanager
  def assertRaisesFireExit(self, code, regexp='.*'):
    """Asserts that a FireExit error is raised in the context.

    Allows tests to check that Fire's wrapper around SystemExit is raised
    and that a regexp is matched in the output.

    Args:
      code: The status code that the FireExit should contain.
      regexp: stdout must match this regex.

    Yields:
      Yields to the wrapped context.
    """
    with self.assertOutputMatches(stderr=regexp):
      with self.assertRaises(core.FireExit):
        try:
          yield
        except core.FireExit as exc:
          if exc.code != code:
            raise AssertionError('Incorrect exit code: %r != %r' %
                                 (exc.code, code))
          self.assertIsInstance(exc.trace, trace.FireTrace)
          raise


@contextlib.contextmanager
def ChangeDirectory(directory):
  """Context manager to mock a directory change and revert on exit."""
  cwdir = os.getcwd()
  os.chdir(directory)

  try:
    yield directory
  finally:
    os.chdir(cwdir)


# pylint: disable=invalid-name
main = unittest.main
skip = unittest.skip
skipIf = unittest.skipIf
# pylint: enable=invalid-name
