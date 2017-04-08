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

"""Test the test utilities for Fire's tests"""

from __future__ import print_function

import sys

from fire import testutils

class TestTestUtils(testutils.BaseTestCase):
  """Let's get meta"""

  def test_no_check_on_exception(self):
    with self.assertRaises(ValueError):
      with self.assertOutputMatches(stdout='blah'):
        raise ValueError()

  def test_check_stdout_or_stderr_none(self):
    with self.assertRaisesRegexp(AssertionError, 'stdout:'):
      with self.assertOutputMatches(stdout=None):
        print('blah')

    with self.assertRaisesRegexp(AssertionError, 'stderr:'):
      with self.assertOutputMatches(stderr=None):
        print('blah', file=sys.stderr)

    with self.assertRaisesRegexp(AssertionError, 'stderr:'):
      with self.assertOutputMatches(stdout='apple', stderr=None):
        print('apple')
        print('blah', file=sys.stderr)

  def test_correct_ordering_of_assert_raises(self):
    # check to make sure FireExit tests are correct
    with self.assertOutputMatches(stdout='confirmed.*not working'):
      with self.assertRaises(ValueError):
        print('''Yep, we've confirmed it.\nThe receiver is not working. :(''')
        raise ValueError()
