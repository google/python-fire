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

from fire import core
from fire import test_components as tc
from fire import trace
import contextlib
import mock
import re
import six
import sys
import unittest


class BaseTest(unittest.TestCase):
  @contextlib.contextmanager
  def assertRaisesFireExit(self, code, regexp=None):
    """Avoids some boiler plate to make it easier to check a system exit is
        raised and regexp is matched"""
    if regexp is None:
      regexp = '.*'
    with self.assertRaises(core.FireExit):
      stdout = six.StringIO()
      with mock.patch.object(sys, 'stdout', stdout):
        try:
          yield
        except core.FireExit as exc:
          assert exc.code == code, 'Incorrect exit code: %r != %r' % (exc.code, code)
          stdout.flush()
          stdout.seek(0)
          value = stdout.getvalue()
          assert re.search(regexp, value, re.DOTALL | re.MULTILINE), 'Expected %r to match %r' % (value, regexp)
          raise


class CoreTest(BaseTest):
  def testOneLineResult(self):
    self.assertEqual(core._OneLineResult(1), '1')
    self.assertEqual(core._OneLineResult('hello'), 'hello')
    self.assertEqual(core._OneLineResult({}), '{}')
    self.assertEqual(core._OneLineResult({'x': 'y'}), '{"x": "y"}')

  @mock.patch('fire.interact.Embed')
  def testInteractiveMode(self, mock_embed):
    core.Fire(tc.TypedProperties, 'alpha')
    self.assertFalse(mock_embed.called)
    core.Fire(tc.TypedProperties, 'alpha -- -i')
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeFullArgument(self, mock_embed):
    core.Fire(tc.TypedProperties, 'alpha -- --interactive')
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariables(self, mock_embed):
    core.Fire(tc.WithDefaults, 'double 2 -- -i')
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertFalse(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariablesWithName(self, mock_embed):
    core.Fire(tc.WithDefaults, 'double 2 -- -i -v', name='D')
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertTrue(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertEqual(variables['D'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  def testImproperUseOfHelp(self):
    # This should produce a help message
    with self.assertRaisesFireExit(2, 'The proper way to show help.*Usage:'):
      self.assertIsNone(core.Fire(tc.TypedProperties, 'alpha --help'))

  def testProperUseOfHelp(self):
    # ape argparse
    with self.assertRaisesFireExit(0, 'Usage:.*upper'):
      core.Fire(tc.TypedProperties, 'gamma -- --help')

  def testInvalidParameterRaisesFireExit(self):
    with self.assertRaisesFireExit(2, 'runmisspelled'):
      core.Fire(tc.Kwargs, 'props --a=1 --b=2 runmisspelled')

  def testErrorRaising(self):
    # Errors in user code should not be caught; they should surface as normal.
    # (this will lead to exit status of 1 in client code)
    with self.assertRaises(ValueError):
      core.Fire(tc.ErrorRaiser, 'fail')

  def testFireError(self):
    error = core.FireError('Example error')
    self.assertIsNotNone(error)

  def testFireErrorMultipleValues(self):
    error = core.FireError('Example error', 'value')
    self.assertIsNotNone(error)

if __name__ == '__main__':
  unittest.main()
