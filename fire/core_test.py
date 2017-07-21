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

"""Tests for the core module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import core
from fire import test_components as tc
from fire import testutils
from fire import trace
import mock


class CoreTest(testutils.BaseTestCase):

  def testOneLineResult(self):
    self.assertEqual(core._OneLineResult(1), '1')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult('hello'), 'hello')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult({}), '{}')  # pylint: disable=protected-access
    self.assertEqual(core._OneLineResult({'x': 'y'}), '{"x": "y"}')  # pylint: disable=protected-access

  def testOneLineResultCircularRef(self):
    circular_reference = tc.CircularReference()
    self.assertEqual(core._OneLineResult(circular_reference.create()),  # pylint: disable=protected-access
                     "{'y': {...}}")

  @mock.patch('fire.interact.Embed')
  def testInteractiveMode(self, mock_embed):
    core.Fire(tc.TypedProperties, command=['alpha'])
    self.assertFalse(mock_embed.called)
    core.Fire(tc.TypedProperties, command=['alpha', '--', '-i'])
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeFullArgument(self, mock_embed):
    core.Fire(tc.TypedProperties, command=['alpha', '--', '--interactive'])
    self.assertTrue(mock_embed.called)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariables(self, mock_embed):
    core.Fire(tc.WithDefaults, command=['double', '2', '--', '-i'])
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertFalse(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  @mock.patch('fire.interact.Embed')
  def testInteractiveModeVariablesWithName(self, mock_embed):
    core.Fire(tc.WithDefaults,
              command=['double', '2', '--', '-i', '-v'], name='D')
    self.assertTrue(mock_embed.called)
    (variables, verbose), unused_kwargs = mock_embed.call_args
    self.assertTrue(verbose)
    self.assertEqual(variables['result'], 4)
    self.assertIsInstance(variables['self'], tc.WithDefaults)
    self.assertEqual(variables['D'], tc.WithDefaults)
    self.assertIsInstance(variables['trace'], trace.FireTrace)

  def testImproperUseOfHelp(self):
    # This should produce a warning explaining the proper use of help.
    with self.assertRaisesFireExit(2, 'The proper way to show help.*Usage:'):
      core.Fire(tc.TypedProperties, command=['alpha', '--help'])

  def testProperUseOfHelp(self):
    with self.assertRaisesFireExit(0, 'Usage:.*upper'):
      core.Fire(tc.TypedProperties, command=['gamma', '--', '--help'])

  def testInvalidParameterRaisesFireExit(self):
    with self.assertRaisesFireExit(2, 'runmisspelled'):
      core.Fire(tc.Kwargs, command=['props', '--a=1', '--b=2', 'runmisspelled'])

  def testErrorRaising(self):
    # Errors in user code should not be caught; they should surface as normal.
    # This will lead to exit status code 1 for the client program.
    with self.assertRaises(ValueError):
      core.Fire(tc.ErrorRaiser, command=['fail'])

  def testFireError(self):
    error = core.FireError('Example error')
    self.assertIsNotNone(error)

  def testFireErrorMultipleValues(self):
    error = core.FireError('Example error', 'value')
    self.assertIsNotNone(error)

  def testPrintEmptyDict(self):
    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.EmptyDictOutput, command=['totally_empty'])
    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.EmptyDictOutput, command=['nothing_printable'])


if __name__ == '__main__':
  testutils.main()
