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

"""Test the test utilities for Fire's tests."""

import sys

from fire import testutils


class TestTestUtils(testutils.BaseTestCase):
  """Let's get meta."""

  def testNoCheckOnException(self):
    with self.assertRaises(ValueError):
      with self.assertOutputMatches(stdout='blah'):
        raise ValueError()

  def testCheckStdoutOrStderrNone(self):
    with self.assertRaisesRegex(AssertionError, 'stdout:'):
      with self.assertOutputMatches(stdout=None):
        print('blah')

    with self.assertRaisesRegex(AssertionError, 'stderr:'):
      with self.assertOutputMatches(stderr=None):
        print('blah', file=sys.stderr)

    with self.assertRaisesRegex(AssertionError, 'stderr:'):
      with self.assertOutputMatches(stdout='apple', stderr=None):
        print('apple')
        print('blah', file=sys.stderr)

  def testCorrectOrderingOfAssertRaises(self):
    # Check to make sure FireExit tests are correct.
    with self.assertOutputMatches(stdout='Yep.*first.*second'):
      with self.assertRaises(ValueError):
        print('Yep, this is the first line.\nThis is the second.')
        raise ValueError()


if __name__ == '__main__':
  testutils.main()
