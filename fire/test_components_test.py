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

"""Tests for the test_components module."""

from fire import test_components as tc
from fire import testutils


class TestComponentsTest(testutils.BaseTestCase):
  """Tests to verify that the test components are importable and okay."""

  def testTestComponents(self):
    self.assertIsNotNone(tc.Empty)
    self.assertIsNotNone(tc.OldStyleEmpty)

  def testNonComparable(self):
    with self.assertRaises(ValueError):
      tc.NonComparable() != 2  # pylint: disable=expression-not-assigned
    with self.assertRaises(ValueError):
      tc.NonComparable() == 2  # pylint: disable=expression-not-assigned


if __name__ == '__main__':
  testutils.main()
