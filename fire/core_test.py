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

"""Tests for the core module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import core
from fire import test_components as tc
from fire import testutils
from fire import trace
import mock

import six


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

  # TODO(dbieber): Use parameterized tests to break up repetitive tests.
  def testHelpWithClass(self):
    with self.assertRaisesFireExit(0, 'SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*ARG1'):
      core.Fire(tc.InstanceVars, command=['-h'])

  def testHelpWithMember(self):
    with self.assertRaisesFireExit(0, 'SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*capitalize'):
      core.Fire(tc.TypedProperties, command=['gamma', '-h'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*delta'):
      core.Fire(tc.TypedProperties, command=['delta', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*echo'):
      core.Fire(tc.TypedProperties, command=['echo', '--help'])

  def testHelpOnErrorInConstructor(self):
    with self.assertRaisesFireExit(0, 'SYNOPSIS.*VALUE'):
      core.Fire(tc.ErrorInConstructor, command=['--', '--help'])
    with self.assertRaisesFireExit(0, 'INFO:.*SYNOPSIS.*VALUE'):
      core.Fire(tc.ErrorInConstructor, command=['--help'])

  def testHelpWithNamespaceCollision(self):
    # Tests cases when calling the help shortcut should not show help.
    with self.assertOutputMatches(stdout='DESCRIPTION.*', stderr=None):
      core.Fire(tc.WithHelpArg, command=['--help', 'False'])
    with self.assertOutputMatches(stdout='help in a dict', stderr=None):
      core.Fire(tc.WithHelpArg, command=['dictionary', '__help'])
    with self.assertOutputMatches(stdout='{}', stderr=None):
      core.Fire(tc.WithHelpArg, command=['dictionary', '--help'])
    with self.assertOutputMatches(stdout='False', stderr=None):
      core.Fire(tc.function_with_help, command=['False'])

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

  def testPrintOrderedDict(self):
    with self.assertOutputMatches(stdout=r'A:\s+A\s+2:\s+2\s+', stderr=None):
      core.Fire(tc.OrderedDictionary, command=['non_empty'])
    with self.assertOutputMatches(stdout='{}'):
      core.Fire(tc.OrderedDictionary, command=['empty'])

  def testPrintNamedTupleField(self):
    with self.assertOutputMatches(stdout='11', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', 'x'])

  def testPrintNamedTupleFieldNameEqualsValue(self):
    with self.assertOutputMatches(stdout='x', stderr=None):
      core.Fire(tc.NamedTuple, command=['matching_names', 'x'])

  def testPrintNamedTupleIndex(self):
    with self.assertOutputMatches(stdout='22', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', '1'])

  def testPrintSet(self):
    with self.assertOutputMatches(stdout='.*three.*', stderr=None):
      core.Fire(tc.simple_set(), command=[])

  def testPrintFrozenSet(self):
    with self.assertOutputMatches(stdout='.*three.*', stderr=None):
      core.Fire(tc.simple_frozenset(), command=[])

  def testPrintNamedTupleNegativeIndex(self):
    with self.assertOutputMatches(stdout='11', stderr=None):
      core.Fire(tc.NamedTuple, command=['point', '-2'])

  def testCallable(self):
    with self.assertOutputMatches(stdout=r'foo:\s+foo\s+', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=['--foo=foo'])
    with self.assertOutputMatches(stdout=r'foo\s+', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=['print_msg', 'foo'])
    with self.assertOutputMatches(stdout=r'', stderr=None):
      core.Fire(tc.CallableWithKeywordArgument(), command=[])

  def testCallableWithPositionalArgs(self):
    with self.assertRaisesFireExit(2, ''):
      # This does not give 7 since positional args are disallowed for callable
      # objects.
      core.Fire(tc.CallableWithPositionalArgs(), command=['3', '4'])

  def testStaticMethod(self):
    self.assertEqual(
        core.Fire(tc.HasStaticAndClassMethods,
                  command=['static_fn', 'alpha']),
        'alpha',
    )

  def testClassMethod(self):
    self.assertEqual(
        core.Fire(tc.HasStaticAndClassMethods,
                  command=['class_fn', '6']),
        7,
    )

  @testutils.skipIf(six.PY2, 'lru_cache is Python 3 only.')
  def testLruCacheDecoratorBoundArg(self):
    self.assertEqual(
        core.Fire(tc.py3.LruCacheDecoratedMethod,  # pytype: disable=module-attr
                  command=['lru_cache_in_class', 'foo']), 'foo')

  @testutils.skipIf(six.PY2, 'lru_cache is Python 3 only.')
  def testLruCacheDecorator(self):
    self.assertEqual(
        core.Fire(tc.py3.lru_cache_decorated,  # pytype: disable=module-attr
                  command=['foo']), 'foo')


if __name__ == '__main__':
  testutils.main()
