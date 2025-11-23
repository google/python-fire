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

"""Tests for the string_tools module."""

from fire import testutils

from examples.string_tools import string_tools


class StringToolsTest(testutils.BaseTestCase):

  def testStringTools(self):
    # reverse
    self.assertEqual(string_tools.reverse("Hello"), "olleh")

    # uppercase
    self.assertEqual(string_tools.uppercase("hello"), "HELLO")

    # count_words
    self.assertEqual(string_tools.count_words("Hello world"), 2)
    self.assertEqual(string_tools.count_words("one two three four"), 4)


if __name__ == '__main__':
  testutils.main()
