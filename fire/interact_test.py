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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
  from cStringIO import StringIO
except ImportError:
  from io import StringIO

from fire import interact
import mock

import unittest


class InteractTest(unittest.TestCase):

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

  @mock.patch('sys.stderr', new_callable=StringIO)
  @mock.patch('sys.stdout', new_callable=StringIO)
  def testEmbedIPythonString(self, mock_stdout, mock_stderr):
    argv = ['-c', 'print(x);']
    interact._EmbedIPython({'x': 'This is a string.'}, argv=argv)
    self.assertIn('This is a string.\n', mock_stdout.getvalue())
    self.assertEqual(mock_stderr.getvalue(), '')

if __name__ == '__main__':
  unittest.main()
