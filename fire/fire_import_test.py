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

"""Tests importing the fire module."""

import sys

import fire
from fire import testutils
import mock


class FireImportTest(testutils.BaseTestCase):
  """Tests importing Fire."""

  def testFire(self):
    with mock.patch.object(sys, 'argv', ['commandname']):
      fire.Fire()

  def testFireMethods(self):
    self.assertIsNotNone(fire.Fire)

  def testNoPrivateMethods(self):
    self.assertTrue(hasattr(fire, 'Fire'))
    self.assertFalse(hasattr(fire, '_Fire'))


if __name__ == '__main__':
  testutils.main()
