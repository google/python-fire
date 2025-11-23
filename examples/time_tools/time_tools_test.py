# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the time_tools module."""

from fire import testutils
from examples.time_tools import time_tools


class TimeToolsTest(testutils.BaseTestCase):

  def testToSeconds(self):
    self.assertEqual(time_tools.to_seconds(1, 30), 90)
    self.assertEqual(time_tools.to_seconds(0, 45), 45)

  def testAddSeconds(self):
    result = time_tools.add_seconds("2024-01-01 10:00:00", 120)
    self.assertEqual(result, "2024-01-01 10:02:00")


if __name__ == "__main__":
  testutils.main()
