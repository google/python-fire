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

"""Tests for the widget module."""

from fire import testutils

from examples.widget import widget


class WidgetTest(testutils.BaseTestCase):

  def testWidgetWhack(self):
    toy = widget.Widget()
    self.assertEqual(toy.whack(), 'whack!')
    self.assertEqual(toy.whack(3), 'whack! whack! whack!')

  def testWidgetBang(self):
    toy = widget.Widget()
    self.assertEqual(toy.bang(), 'bang bang!')
    self.assertEqual(toy.bang('boom'), 'boom bang!')


if __name__ == '__main__':
  testutils.main()
