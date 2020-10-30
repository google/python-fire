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
import tempfile

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
      __main__.main(
          ['__main__.py', 'os.path', 'join', 'part1', 'part2', 'part3'])
    with self.assertOutputMatches('%s\n' % expected):
      __main__.main(
          ['__main__.py', 'os', 'path', '-', 'join', 'part1', 'part2', 'part3'])


class MainModuleFileTest(testutils.BaseTestCase):
  """Tests to verify correct import behavior for file executables."""

  def setUp(self):
    super(MainModuleFileTest, self).setUp()
    self.file = tempfile.NamedTemporaryFile(suffix='.py')
    self.file.write(b'class Foo:\n  def double(self, n):\n    return 2 * n\n')
    self.file.flush()

    self.file2 = tempfile.NamedTemporaryFile()

  def testFileNameFire(self):
    # Confirm that the file is correctly imported and doubles the number.
    with self.assertOutputMatches('4'):
      __main__.main(
          ['__main__.py', self.file.name, 'Foo', 'double', '--n', '2'])

  def testFileNameFailure(self):
    # Confirm that an existing file without a .py suffix raises a ValueError.
    with self.assertRaises(ValueError):
      __main__.main(
          ['__main__.py', self.file2.name, 'Foo', 'double', '--n', '2'])

  def testFileNameModuleDuplication(self):
    # Confirm that a file that masks a module still loads the module.
    with self.assertOutputMatches('gettempdir'):
      dirname = os.path.dirname(self.file.name)
      with testutils.ChangeDirectory(dirname):
        with open('tempfile', 'w'):
          __main__.main([
              '__main__.py',
              'tempfile',
          ])

        os.remove('tempfile')

  def testFileNameModuleFileFailure(self):
    # Confirm that an invalid file that masks a non-existent module fails.
    with self.assertRaisesRegex(ValueError,
                                r'Fire can only be called on \.py files\.'):  # pylint: disable=line-too-long,  # pytype: disable=attribute-error
      dirname = os.path.dirname(self.file.name)
      with testutils.ChangeDirectory(dirname):
        with open('foobar', 'w'):
          __main__.main([
              '__main__.py',
              'foobar',
          ])

        os.remove('foobar')


if __name__ == '__main__':
  testutils.main()
