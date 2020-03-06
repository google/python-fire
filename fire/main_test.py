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

"""Test using Fire via `python -m fire`."""

import os

from fire import __main__
from fire import testutils


class MainModuleTest(testutils.BaseTestCase):
  """Tests to verify the behavior of __main__ (python -m fire)."""

  def testNameSetting(self):
    # Confirm one of the usage lines has the gettempdir member.
    with self.assertOutputMatches('gettempdir'):
      __main__.main(['__main__.py', 'tempfile'])

  def testArgPassing(self):
    expected = os.path.join('part1', 'part2', 'part3')
    with self.assertOutputMatches('%s\n' % expected):
      __main__.main(['__main__.py', 'os.path', 'join', 'part1', 'part2',
                     'part3'])
    with self.assertOutputMatches('%s\n' % expected):
      __main__.main(['__main__.py', 'os', 'path', '-', 'join', 'part1',
                     'part2', 'part3'])


if __name__ == '__main__':
  testutils.main()
