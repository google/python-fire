# Copyright (C) 2026 Google LLC.
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

"""Tests for Windows ANSI initialization behavior."""

from unittest import mock

from fire import formatting_windows
from fire import testutils


class FormattingWindowsTest(testutils.BaseTestCase):

  def test_git_bash_skips_colorama(self):
    for msystem in ('MINGW64', 'MINGW32', 'MSYS', 'mingw64'):
      with self.subTest(msystem=msystem):
        with mock.patch.dict('os.environ', {'MSYSTEM': msystem}):
          with mock.patch.object(formatting_windows, 'HAS_COLORAMA', True):
            with mock.patch.object(formatting_windows, 'colorama',
                                   create=True) as colorama:
              with mock.patch.object(formatting_windows.platform, 'release',
                                     side_effect=AssertionError('not needed')):
                formatting_windows.initialize_or_disable()
                colorama.init.assert_not_called()

  def test_non_git_bash_keeps_colorama_initialization(self):
    with mock.patch.dict('os.environ', {}, clear=True):
      with mock.patch.object(formatting_windows, 'HAS_COLORAMA', True):
        with mock.patch.object(formatting_windows, 'colorama',
                               create=True) as colorama:
          with mock.patch.object(formatting_windows.platform, 'release',
                                 return_value='11'):
            formatting_windows.initialize_or_disable()
            colorama.init.assert_called_once_with(wrap=True)

  def test_missing_colorama_disables_colors_outside_git_bash(self):
    with mock.patch.dict('os.environ', {}, clear=True):
      with mock.patch.object(formatting_windows, 'HAS_COLORAMA', False):
        formatting_windows.initialize_or_disable()
        self.assertEqual('1', formatting_windows.os.environ['ANSI_COLORS_DISABLED'])


if __name__ == '__main__':
  testutils.main()
