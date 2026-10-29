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

from unittest import mock

from fire import formatting
from fire import formatting_windows
from fire import testutils

LINE_LENGTH = 80


class FormattingTest(testutils.BaseTestCase):

  def test_bold(self):
    text = formatting.Bold('hello')
    self.assertIn(text, ['hello', '\x1b[1mhello\x1b[0m'])

  def test_underline(self):
    text = formatting.Underline('hello')
    self.assertIn(text, ['hello', '\x1b[4mhello\x1b[0m'])

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

  def test_ellipsis_truncate(self):
    text = 'This is a string'
    truncated_text = formatting.EllipsisTruncate(
        text=text, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual('This is...', truncated_text)

  def test_ellipsis_truncate_not_enough_space(self):
    text = 'This is a string'
    truncated_text = formatting.EllipsisTruncate(
        text=text, available_space=2, line_length=LINE_LENGTH)
    self.assertEqual('This is a string', truncated_text)

  def test_ellipsis_middle_truncate(self):
    text = '1000000000L'
    truncated_text = formatting.EllipsisMiddleTruncate(
        text=text, available_space=7, line_length=LINE_LENGTH)
    self.assertEqual('10...0L', truncated_text)

  def test_ellipsis_middle_truncate_not_enough_space(self):
    text = '1000000000L'
    truncated_text = formatting.EllipsisMiddleTruncate(
        text=text, available_space=2, line_length=LINE_LENGTH)
    self.assertEqual('1000000000L', truncated_text)


class FormattingWindowsTest(testutils.BaseTestCase):

  def test_std_output_handle_constant(self):
    self.assertEqual(formatting_windows.STD_OUTPUT_HANDLE, -11)

  @mock.patch.object(formatting_windows, 'HAS_COLORAMA', True)
  @mock.patch.object(formatting_windows, 'colorama', create=True)
  @mock.patch('platform.release', return_value='10')
  @mock.patch('sys.stdout.isatty', return_value=True)
  def test_initialize_or_disable_windows_10(
      self, mock_isatty, mock_release, mock_colorama
  ):
    fake_kernel32 = mock.MagicMock()
    fake_kernel32.GetStdHandle.return_value = 42
    fake_kernel32.GetConsoleMode.return_value = 1
    fake_kernel32.SetConsoleMode.return_value = 1

    with mock.patch.object(
        formatting_windows.ctypes, 'windll', create=True
    ) as mock_windll:
      mock_windll.kernel32 = fake_kernel32
      with mock.patch.object(
          formatting_windows.ctypes, 'wintypes', create=True
      ) as mock_wintypes:
        with mock.patch.object(
            formatting_windows.ctypes, 'byref', return_value=mock.MagicMock()
        ):
          mock_dword = mock.MagicMock()
          mock_dword.value = 0
          mock_wintypes.DWORD.return_value = mock_dword

          formatting_windows.initialize_or_disable()

          fake_kernel32.GetStdHandle.assert_called_once_with(
              formatting_windows.STD_OUTPUT_HANDLE
          )
          mock_colorama.init.assert_called_once_with(wrap=False)


if __name__ == '__main__':
  testutils.main()
