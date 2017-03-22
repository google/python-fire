# Copyright (C) 2017 Google Inc.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib
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
  def assertRaisesFireExit(self, code, regexp=None):
    """Asserts that a FireExit error is raised in the context.

    Allows tests to check that Fire's wrapper around SystemExit is raised
    and that a regexp is matched in the output.

    Args:
      code: The status code that the FireExit should contain.
      regexp: stdout must match this regex.
    Yields:
      Yields to the wrapped context.
    """
    if regexp is None:
      regexp = '.*'
    with self.assertRaises(core.FireExit):
      stdout = six.StringIO()
      with mock.patch.object(sys, 'stdout', stdout):
        try:
          yield
        except core.FireExit as exc:
          if exc.code != code:
            raise AssertionError('Incorrect exit code: %r != %r' % (exc.code,
                                                                    code))
          self.assertIsInstance(exc.trace, trace.FireTrace)
          stdout.flush()
          stdout.seek(0)
          value = stdout.getvalue()
          if not re.search(regexp, value, re.DOTALL | re.MULTILINE):
            raise AssertionError('Expected %r to match %r' % (value, regexp))
          raise
