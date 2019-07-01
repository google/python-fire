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

"""Tests for the fire module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import unittest

import fire
from fire import test_components as tc
from fire import testutils

import mock
import six


class FireTest(testutils.BaseTestCase):

  def testFire(self):
    with mock.patch.object(sys, 'argv', ['progname']):
      fire.Fire(tc.Empty)
      fire.Fire(tc.OldStyleEmpty)
      fire.Fire(tc.WithInit)
    # Test both passing command as a sequence and as a string.
    self.assertEqual(fire.Fire(tc.NoDefaults, command='triple 4'), 12)
    self.assertEqual(fire.Fire(tc.WithDefaults, command=('double', '2')), 4)
    self.assertEqual(fire.Fire(tc.WithDefaults, command=['triple', '4']), 12)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults,
                               command=['double', '2']), 4)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults,
                               command=['triple', '4']), 12)

  def testFirePositionalCommand(self):
    # Test passing command as a positional argument.
    self.assertEqual(fire.Fire(tc.NoDefaults, 'double 2'), 4)
    self.assertEqual(fire.Fire(tc.NoDefaults, ['double', '2']), 4)

  def testFireInvalidCommandArg(self):
    with self.assertRaises(ValueError):
      # This is not a valid command.
      fire.Fire(tc.WithDefaults, command=10)

  def testFireDefaultName(self):
    with mock.patch.object(sys, 'argv',
                           [os.path.join('python-fire', 'fire',
                                         'base_filename.py')]):
      with self.assertOutputMatches(stdout='SYNOPSIS.*base_filename.py',
                                    stderr=None):
        fire.Fire(tc.Empty)

  def testFireNoArgs(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['ten']), 10)

  def testFireExceptions(self):
    # Exceptions of Fire are printed to stderr and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.Empty, command=['nomethod'])  # Member doesn't exist.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.NoDefaults, command=['double'])  # Missing argument.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.TypedProperties, command=['delta', 'x'])  # Missing key.

    # Exceptions of the target components are still raised.
    with self.assertRaises(ZeroDivisionError):
      fire.Fire(tc.NumberDefaults, command=['reciprocal', '0.0'])

  def testFireNamedArgs(self):
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '--count', '5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '--count', '5']), 15)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['double', '--count', '5']),
        10)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['triple', '--count', '5']),
        15)

  def testFireNamedArgsSingleHyphen(self):
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '-count', '5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '-count', '5']), 15)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['double', '-count', '5']),
        10)
    self.assertEqual(
        fire.Fire(tc.OldStyleWithDefaults, command=['triple', '-count', '5']),
        15)

  def testFireNamedArgsWithEquals(self):
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '--count=5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '--count=5']), 15)

  def testFireNamedArgsWithEqualsSingleHyphen(self):
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['double', '-count=5']), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults,
                               command=['triple', '-count=5']), 15)

  def testFireAllNamedArgs(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum', '1', '2']), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--alpha', '1', '2']), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--beta', '1', '2']), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '1', '--alpha', '2']), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '1', '--beta', '2']), 5)
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '1', '--beta', '2']), 5)
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--beta', '1', '--alpha', '2']), 4)

  def testFireAllNamedArgsOneMissing(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum']), 0)
    self.assertEqual(fire.Fire(tc.MixedDefaults, command=['sum', '1']), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--alpha', '1']), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['sum', '--beta', '2']), 4)

  def testFirePartialNamedArgs(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '1', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '1', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--beta', '1', '2']), (2, 1))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '1', '--alpha', '2']), (2, 1))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '1', '--beta', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--alpha', '1', '--beta', '2']), (1, 2))
    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--beta', '1', '--alpha', '2']), (2, 1))

  def testFirePartialNamedArgsOneMissing(self):
    # Errors are written to standard out and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults,
                command=['identity'])  # Identity needs an arg.

    with self.assertRaisesFireExit(2):
      # Identity needs a value for alpha.
      fire.Fire(tc.MixedDefaults, command=['identity', '--beta', '2'])

    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '1']), (1, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '--alpha', '1']),
        (1, '0'))

  def testFireAnnotatedArgs(self):
    self.assertEqual(fire.Fire(tc.Annotations, command=['double', '5']), 10)
    self.assertEqual(fire.Fire(tc.Annotations, command=['triple', '5']), 15)

  @unittest.skipIf(six.PY2, 'Keyword-only arguments not in Python 2.')
  def testFireKeywordOnlyArgs(self):
    with self.assertRaisesFireExit(2):
      # Keyword arguments must be passed with flag syntax.
      fire.Fire(tc.py3.KeywordOnly, command=['double', '5'])

    self.assertEqual(
        fire.Fire(tc.py3.KeywordOnly, command=['double', '--count', '5']), 10)
    self.assertEqual(
        fire.Fire(tc.py3.KeywordOnly, command=['triple', '--count', '5']), 15)

  def testFireProperties(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['alpha']), True)
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['beta']), (1, 2, 3))

  def testFireRecursion(self):
    self.assertEqual(
        fire.Fire(tc.TypedProperties,
                  command=['charlie', 'double', 'hello']), 'hellohello')
    self.assertEqual(fire.Fire(tc.TypedProperties,
                               command=['charlie', 'triple', 'w']), 'www')

  def testFireVarArgs(self):
    self.assertEqual(
        fire.Fire(tc.VarArgs,
                  command=['cumsums', 'a', 'b', 'c', 'd']),
        ['a', 'ab', 'abc', 'abcd'])
    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['cumsums', '1', '2', '3', '4']),
        [1, 3, 6, 10])

  def testFireVarArgsWithNamedArgs(self):
    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['varchars', '1', '2', 'c', 'd']),
        (1, 2, 'cd'))
    self.assertEqual(
        fire.Fire(tc.VarArgs, command=['varchars', '3', '4', 'c', 'd', 'e']),
        (3, 4, 'cde'))

  def testFireKeywordArgs(self):
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--name', 'David', '--age', '24']),
        {'name': 'David', 'age': 24})
    # Run this test both with a list command and a string command.
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--message',
                     '"This is a message it has -- in it"']),  # Quotes stripped
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['props', '--message',
                     'This is a message it has -- in it']),
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command='props --message "This is a message it has -- in it"'),
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(
        fire.Fire(tc.Kwargs,
                  command=['upper', '--alpha', 'A', '--beta', 'B']),
        'ALPHA BETA')
    self.assertEqual(
        fire.Fire(
            tc.Kwargs,
            command=['upper', '--alpha', 'A', '--beta', 'B', '-', 'lower']),
        'alpha beta')

  def testFireKeywordArgsWithMissingPositionalArgs(self):
    self.assertEqual(
        fire.Fire(tc.Kwargs, command=['run', 'Hello', 'World', '--cell', 'is']),
        ('Hello', 'World', {'cell': 'is'}))
    self.assertEqual(
        fire.Fire(tc.Kwargs, command=['run', 'Hello', '--cell', 'ok']),
        ('Hello', None, {'cell': 'ok'}))

  def testFireObject(self):
    self.assertEqual(
        fire.Fire(tc.WithDefaults(), command=['double', '--count', '5']), 10)
    self.assertEqual(
        fire.Fire(tc.WithDefaults(), command=['triple', '--count', '5']), 15)

  def testFireDict(self):
    component = {
        'double': lambda x=0: 2 * x,
        'cheese': 'swiss',
    }
    self.assertEqual(fire.Fire(component, command=['double', '5']), 10)
    self.assertEqual(fire.Fire(component, command=['cheese']), 'swiss')

  def testFireObjectWithDict(self):
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'echo']), 'E')
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'echo', 'lower']), 'e')
    self.assertIsInstance(
        fire.Fire(tc.TypedProperties, command=['delta', 'nest']), dict)
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['delta', 'nest', '0']), 'a')

  def testFireSet(self):
    component = tc.simple_set()
    result = fire.Fire(component, command=[])
    self.assertEqual(len(result), 3)

  def testFireFrozenset(self):
    component = tc.simple_frozenset()
    result = fire.Fire(component, command=[])
    self.assertEqual(len(result), 3)

  def testFireList(self):
    component = ['zero', 'one', 'two', 'three']
    self.assertEqual(fire.Fire(component, command=['2']), 'two')
    self.assertEqual(fire.Fire(component, command=['3']), 'three')
    self.assertEqual(fire.Fire(component, command=['-1']), 'three')

  def testFireObjectWithList(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['echo', '0']),
                     'alex')
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['echo', '1']),
                     'bethany')

  def testFireObjectWithTuple(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['fox', '0']),
                     'carry')
    self.assertEqual(fire.Fire(tc.TypedProperties, command=['fox', '1']),
                     'divide')

  def testFireObjectWithListAsObject(self):
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['echo', 'count', 'bethany']),
        1)

  def testFireObjectWithTupleAsObject(self):
    self.assertEqual(
        fire.Fire(tc.TypedProperties, command=['fox', 'count', 'divide']),
        1)

  def testFireNoComponent(self):
    self.assertEqual(fire.Fire(command=['tc', 'WithDefaults', 'double', '10']),
                     20)
    last_char = lambda text: text[-1]  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command=['last_char', '"Hello"']), 'o')
    self.assertEqual(fire.Fire(command=['last-char', '"World"']), 'd')
    rset = lambda count=0: set(range(count))  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command=['rset', '5']), {0, 1, 2, 3, 4})

  def testFireUnderscores(self):
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore-example']), 'fish fingers')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_example']), 'fish fingers')

  def testFireUnderscoresInArg(self):
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore-function', 'example']), 'example')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_function', '--underscore-arg=score']),
        'score')
    self.assertEqual(
        fire.Fire(tc.Underscores,
                  command=['underscore_function', '--underscore_arg=score']),
        'score')

  def testBoolParsing(self):
    self.assertEqual(fire.Fire(tc.BoolConverter, command=['as-bool', 'True']),
                     True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', 'False']), False)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--arg=True']), True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--arg=False']), False)
    self.assertEqual(fire.Fire(tc.BoolConverter, command=['as-bool', '--arg']),
                     True)
    self.assertEqual(
        fire.Fire(tc.BoolConverter, command=['as-bool', '--noarg']), False)

  def testBoolParsingContinued(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', 'True', 'False']), (True, False))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha=False', '10']), (False, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta', '10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--noalpha', '--beta']), (False, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=['identity', '10', '--beta']),
        (10, True))

  def testBoolParsingSingleHyphen(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha=False', '10']), (False, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-beta', '10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-noalpha', '-beta']), (False, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-alpha', '-10', '-beta']), (-10, True))

  def testBoolParsingLessExpectedCases(self):
    # Note: Does not return (True, 10).
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '10']), (10, '0'))
    # To get (True, 10), use one of the following:
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', '--beta=10']),
        (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', 'True', '10']), (True, 10))

    # Note: Does not return (True, '--test') or ('--test', 0).
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, command=['identity', '--alpha', '--test'])

    self.assertEqual(
        fire.Fire(
            tc.MixedDefaults,
            command=['identity', '--alpha', 'True', '"--test"']),
        (True, '--test'))
    # To get ('--test', '0'), use one of the following:
    self.assertEqual(fire.Fire(tc.MixedDefaults,
                               command=['identity', '--alpha=--test']),
                     ('--test', '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, command=r'identity --alpha \"--test\"'),
        ('--test', '0'))

  def testSingleCharFlagParsing(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a']), (True, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '--beta=10']), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '-b']), (True, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b']), (42, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b', '10']), (42, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '--alpha', 'True', '-b', '10']),
        (True, 10))
    with self.assertRaisesFireExit(2):
      # This test attempts to use an ambiguous shortcut flag on a function with
      # a naming conflict for the shortcut, triggering a FireError.
      fire.Fire(tc.SimilarArgNames, command=['identity', '-b'])

  def testSingleCharFlagParsingEqualSign(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=True']), (True, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=3', '--beta=10']), (3, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=False', '-b=15']), (False, 15))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a', '42', '-b=12']), (42, 12))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-a=42', '-b', '10']), (42, 10))

  def testSingleCharFlagParsingExactMatch(self):
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a']), (True, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a=10']), (10, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '--a']), (True, None))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-alpha']), (None, True))
    self.assertEqual(
        fire.Fire(tc.SimilarArgNames,
                  command=['identity2', '-a', '-alpha']), (True, True))

  def testSingleCharFlagParsingCapitalLetter(self):
    self.assertEqual(
        fire.Fire(tc.CapitalizedArgNames,
                  command=['sum', '-D', '5', '-G', '10']), 15)

  def testBoolParsingWithNo(self):
    # In these examples --nothing always refers to the nothing argument:
    def fn1(thing, nothing):
      return thing, nothing

    self.assertEqual(fire.Fire(fn1, command=['--thing', '--nothing']),
                     (True, True))
    self.assertEqual(fire.Fire(fn1, command=['--thing', '--nonothing']),
                     (True, False))

    with self.assertRaisesFireExit(2):
      # In this case nothing=False (since rightmost setting of a flag gets
      # precedence), but it errors because thing has no value.
      fire.Fire(fn1, command=['--nothing', '--nonothing'])

    # In these examples, --nothing sets thing=False:
    def fn2(thing, **kwargs):
      return thing, kwargs
    self.assertEqual(fire.Fire(fn2, command=['--thing']), (True, {}))
    self.assertEqual(fire.Fire(fn2, command=['--nothing']), (False, {}))
    with self.assertRaisesFireExit(2):
      # In this case, nothing=True, but it errors because thing has no value.
      fire.Fire(fn2, command=['--nothing=True'])
    self.assertEqual(fire.Fire(fn2, command=['--nothing', '--nothing=True']),
                     (False, {'nothing': True}))

    def fn3(arg, **kwargs):
      return arg, kwargs
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--thing']),
                     ('value', {'thing': True}))
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--nothing']),
                     ('value', {'thing': False}))
    self.assertEqual(fire.Fire(fn3, command=['--arg=value', '--nonothing']),
                     ('value', {'nothing': False}))

  def testTraceFlag(self):
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '--trace'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-t'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, command=['--', '--trace'])

  def testHelpFlag(self):
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '--help'])
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-h'])
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, command=['--', '--help'])

  def testHelpFlagAndTraceFlag(self):
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter,
                command=['as-bool', 'True', '--', '--help', '--trace'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter, command=['as-bool', 'True', '--', '-h', '-t'])
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*SYNOPSIS'):
      fire.Fire(tc.BoolConverter, command=['--', '-h', '--trace'])

  def testTabCompletionNoName(self):
    completion_script = fire.Fire(tc.NoDefaults, command=['--', '--completion'])
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletion(self):
    completion_script = fire.Fire(
        tc.NoDefaults, command=['--', '--completion'], name='c')
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletionWithDict(self):
    actions = {'multiply': lambda a, b: a * b}
    completion_script = fire.Fire(
        actions, command=['--', '--completion'], name='actCLI')
    self.assertIn('actCLI', completion_script)
    self.assertIn('multiply', completion_script)

  def testBasicSeparator(self):
    # '-' is the default separator.
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '+', '_']), ('+', '_'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '_', '+', '-']), ('_', '+'))

    # If we change the separator we can use '-' as an argument.
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['identity', '-', '_', '--', '--separator', '&']),
        ('-', '_'))

    # The separator triggers a function call, but there aren't enough arguments.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, command=['identity', '-', '_', '+'])

  def testNonComparable(self):
    """Fire should work with classes that disallow comparisons."""
    # Make sure this test passes both with a string command or a list command.
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=''), tc.NonComparable)
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=[]), tc.NonComparable)

    # The first separator instantiates the NonComparable object.
    # The second separator causes Fire to check if the separator was necessary.
    self.assertIsInstance(
        fire.Fire(tc.NonComparable, command=['-', '-']), tc.NonComparable)

  def testExtraSeparators(self):
    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', '-', 'as-bool', 'True']),
        True)
    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', '-', '-', 'as-bool',
                     'True']),
        True)

  def testSeparatorForChaining(self):
    # Without a separator all args are consumed by get_obj.
    self.assertIsInstance(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', 'arg2', 'as-bool', 'True']),
        tc.BoolConverter)
    # With a separator only the preceding args are consumed by get_obj.
    self.assertEqual(
        fire.Fire(
            tc.ReturnsObj,
            command=['get-obj', 'arg1', 'arg2', '-', 'as-bool', 'True']), True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', 'arg2', '&', 'as-bool', 'True',
                           '--', '--separator', '&']),
        True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  command=['get-obj', 'arg1', '$$', 'as-bool', 'True', '--',
                           '--separator', '$$']),
        True)

  def testNegativeNumbers(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '-3', '--beta', '-4']), -11)

  def testFloatForExpectedInt(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults,
                  command=['sum', '--alpha', '2.2', '--beta', '3.0']), 8.2)
    self.assertEqual(
        fire.Fire(
            tc.NumberDefaults,
            command=['integer_reciprocal', '--divisor', '5.0']), 0.2)
    self.assertEqual(
        fire.Fire(tc.NumberDefaults, command=['integer_reciprocal', '4.0']),
        0.25)

  def testClassInstantiation(self):
    self.assertIsInstance(fire.Fire(tc.InstanceVars,
                                    command=['--arg1=a1', '--arg2=a2']),
                          tc.InstanceVars)
    with self.assertRaisesFireExit(2):
      # Cannot instantiate a class with positional args.
      fire.Fire(tc.InstanceVars, command=['a1', 'a2'])

  def testTraceErrors(self):
    # Class needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['--arg1=a1'])

    # Routine needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1', 'a2', '-', 'run', 'b1'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars,
                command=['--arg1=a1', '--arg2=a2', '-', 'run b1'])

    # Extra args cannot be consumed.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars,
                command=['a1', 'a2', '-', 'run', 'b1', 'b2', 'b3'])
    with self.assertRaisesFireExit(2):
      fire.Fire(
          tc.InstanceVars,
          command=['--arg1=a1', '--arg2=a2', '-', 'run', 'b1', 'b2', 'b3'])

    # Cannot find member to access.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['a1', 'a2', '-', 'jog'])
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, command=['--arg1=a1', '--arg2=a2', '-', 'jog'])


if __name__ == '__main__':
  testutils.main()
