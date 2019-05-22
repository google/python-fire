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

"""Tests for formatting.py."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import formatting
from fire import testutils


class FormattingTest(testutils.BaseTestCase):

  def test_bold(self):
    text = formatting.Bold('hello')
    self.assertEqual('\x1b[1mhello\x1b[0m', text)

  def test_underline(self):
    text = formatting.Underline('hello')
    self.assertEqual('\x1b[4mhello\x1b[0m', text)

  def test_indent(self):
    text = formatting.Indent('hello', spaces=2)
    self.assertEqual('  hello', text)

  def test_indent_multiple_lines(self):
    text = formatting.Indent('hello\nworld', spaces=2)
    self.assertEqual('  hello\n  world', text)

  def test_wrap_one_item(self):
    lines = formatting.WrappedJoin(['rice'])
    self.assertEqual(['rice'], lines)

  def test_wrap_multiple_items(self):
    lines = formatting.WrappedJoin(['rice', 'beans', 'chicken', 'cheese'],
                                   width=15)
    self.assertEqual(['rice | beans |',
                      'chicken |',
                      'cheese'], lines)


if __name__ == '__main__':
  testutils.main()
