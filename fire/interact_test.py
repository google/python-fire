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

"""Tests for the interact module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import interact
from fire import testutils

import mock


class InteractTest(testutils.BaseTestCase):

  @mock.patch('IPython.start_ipython')
  def testInteract(self, mock_ipython):
    self.assertFalse(mock_ipython.called)
    interact.Embed({})
    self.assertTrue(mock_ipython.called)

  @mock.patch('IPython.start_ipython')
  def testInteractVariables(self, mock_ipython):
    self.assertFalse(mock_ipython.called)
    interact.Embed({
        'count': 10,
        'mock': mock,
    })
    self.assertTrue(mock_ipython.called)

if __name__ == '__main__':
  testutils.main()
