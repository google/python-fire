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
    self.assertEqual(fire.Fire(tc.NoDefaults, 'double 2'), 4)
    self.assertEqual(fire.Fire(tc.NoDefaults, 'triple 4'), 12)
    self.assertEqual(fire.Fire(tc.WithDefaults, 'double 2'), 4)
    self.assertEqual(fire.Fire(tc.WithDefaults, 'triple 4'), 12)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults, 'double 2'), 4)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults, 'triple 4'), 12)

  def testFireDefaultName(self):
    with mock.patch.object(sys, 'argv',
                           [os.path.join('python-fire', 'fire',
                                         'base_filename.py')]):
      with self.assertOutputMatches(stdout='Usage:       base_filename.py',
                                    stderr=None):
        fire.Fire(tc.Empty)

  def testFireNoArgs(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'ten'), 10)

  def testFireExceptions(self):
    # Exceptions of Fire are printed to stderr and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.Empty, 'nomethod')  # Member doesn't exist.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.NoDefaults, 'double')  # Missing argument.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.TypedProperties, 'delta x')  # Missing key.

    # Exceptions of the target components are still raised.
    with self.assertRaises(ZeroDivisionError):
      fire.Fire(tc.NumberDefaults, 'reciprocal 0.0')

  def testFireNamedArgs(self):
    self.assertEqual(fire.Fire(tc.WithDefaults, 'double --count 5'), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults, 'triple --count 5'), 15)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults, 'double --count 5'), 10)
    self.assertEqual(fire.Fire(tc.OldStyleWithDefaults, 'triple --count 5'), 15)

  def testFireNamedArgsWithEquals(self):
    self.assertEqual(fire.Fire(tc.WithDefaults, 'double --count=5'), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults, 'triple --count=5'), 15)

  def testFireAllNamedArgs(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum 1 2'), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --alpha 1 2'), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --beta 1 2'), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum 1 --alpha 2'), 4)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum 1 --beta 2'), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --alpha 1 --beta 2'), 5)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --beta 1 --alpha 2'), 4)

  def testFireAllNamedArgsOneMissing(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum'), 0)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum 1'), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --alpha 1'), 1)
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'sum --beta 2'), 4)

  def testFirePartialNamedArgs(self):
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity 1 2'), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha 1 2'), (1, 2))
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity --beta 1 2'), (2, 1))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity 1 --alpha 2'), (2, 1))
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity 1 --beta 2'), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha 1 --beta 2'), (1, 2))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --beta 1 --alpha 2'), (2, 1))

  def testFirePartialNamedArgsOneMissing(self):
    # Errors are written to standard out and a FireExit is raised.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, 'identity')  # Identity needs an arg.

    with self.assertRaisesFireExit(2):
      # Identity needs a value for alpha.
      fire.Fire(tc.MixedDefaults, 'identity --beta 2')

    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity 1'), (1, '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha 1'), (1, '0'))

  def testFireAnnotatedArgs(self):
    self.assertEqual(fire.Fire(tc.Annotations, 'double 5'), 10)
    self.assertEqual(fire.Fire(tc.Annotations, 'triple 5'), 15)

  @unittest.skipIf(six.PY2, 'Keyword-only arguments not in Python 2.')
  def testFireKeywordOnlyArgs(self):
    with self.assertRaisesFireExit(2):
      # Keyword arguments must be passed with flag syntax.
      fire.Fire(tc.py3.KeywordOnly, 'double 5')

    self.assertEqual(fire.Fire(tc.py3.KeywordOnly, 'double --count 5'), 10)
    self.assertEqual(fire.Fire(tc.py3.KeywordOnly, 'triple --count 5'), 15)

  def testFireProperties(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, 'alpha'), True)
    self.assertEqual(fire.Fire(tc.TypedProperties, 'beta'), (1, 2, 3))

  def testFireRecursion(self):
    self.assertEqual(
        fire.Fire(tc.TypedProperties, 'charlie double hello'), 'hellohello')
    self.assertEqual(fire.Fire(tc.TypedProperties, 'charlie triple w'), 'www')

  def testFireVarArgs(self):
    self.assertEqual(
        fire.Fire(tc.VarArgs, 'cumsums a b c d'), ['a', 'ab', 'abc', 'abcd'])
    self.assertEqual(fire.Fire(tc.VarArgs, 'cumsums 1 2 3 4'), [1, 3, 6, 10])

  def testFireVarArgsWithNamedArgs(self):
    self.assertEqual(fire.Fire(tc.VarArgs, 'varchars 1 2 c d'), (1, 2, 'cd'))
    self.assertEqual(fire.Fire(tc.VarArgs, 'varchars 3 4 c d e'), (3, 4, 'cde'))

  def testFireKeywordArgs(self):
    self.assertEqual(fire.Fire(tc.Kwargs, 'props --name David --age 24'),
                     {'name': 'David', 'age': 24})
    self.assertEqual(
        fire.Fire(tc.Kwargs,
                  'props --message "This is a message it has -- in it"'),
        {'message': 'This is a message it has -- in it'})
    self.assertEqual(fire.Fire(tc.Kwargs, 'upper --alpha A --beta B'),
                     'ALPHA BETA')
    self.assertEqual(fire.Fire(tc.Kwargs, 'upper --alpha A --beta B - lower'),
                     'alpha beta')

  def testFireKeywordArgsWithMissingPositionalArgs(self):
    self.assertEqual(fire.Fire(tc.Kwargs, 'run Hello World --cell is'),
                     ('Hello', 'World', {'cell': 'is'}))
    self.assertEqual(fire.Fire(tc.Kwargs, 'run Hello --cell ok'),
                     ('Hello', None, {'cell': 'ok'}))

  def testFireObject(self):
    self.assertEqual(fire.Fire(tc.WithDefaults(), 'double --count 5'), 10)
    self.assertEqual(fire.Fire(tc.WithDefaults(), 'triple --count 5'), 15)

  def testFireDict(self):
    component = {
        'double': lambda x=0: 2 * x,
        'cheese': 'swiss',
    }
    self.assertEqual(fire.Fire(component, 'double 5'), 10)
    self.assertEqual(fire.Fire(component, 'cheese'), 'swiss')

  def testFireObjectWithDict(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, 'delta echo'), 'E')
    self.assertEqual(fire.Fire(tc.TypedProperties, 'delta echo lower'), 'e')
    self.assertIsInstance(fire.Fire(tc.TypedProperties, 'delta nest'), dict)
    self.assertEqual(fire.Fire(tc.TypedProperties, 'delta nest 0'), 'a')

  def testFireList(self):
    component = ['zero', 'one', 'two', 'three']
    self.assertEqual(fire.Fire(component, '2'), 'two')
    self.assertEqual(fire.Fire(component, '3'), 'three')
    self.assertEqual(fire.Fire(component, '-1'), 'three')

  def testFireObjectWithList(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, 'echo 0'), 'alex')
    self.assertEqual(fire.Fire(tc.TypedProperties, 'echo 1'), 'bethany')

  def testFireObjectWithTuple(self):
    self.assertEqual(fire.Fire(tc.TypedProperties, 'fox 0'), 'carry')
    self.assertEqual(fire.Fire(tc.TypedProperties, 'fox 1'), 'divide')

  def testFireNoComponent(self):
    self.assertEqual(fire.Fire(command='tc WithDefaults double 10'), 20)
    last_char = lambda text: text[-1]  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command='last_char "Hello"'), 'o')
    self.assertEqual(fire.Fire(command='last-char "World"'), 'd')
    rset = lambda count=0: set(range(count))  # pylint: disable=unused-variable
    self.assertEqual(fire.Fire(command='rset 5'), {0, 1, 2, 3, 4})

  def testFireUnderscores(self):
    self.assertEqual(
        fire.Fire(tc.Underscores, 'underscore-example'), 'fish fingers')
    self.assertEqual(
        fire.Fire(tc.Underscores, 'underscore_example'), 'fish fingers')

  def testFireUnderscoresInArg(self):
    self.assertEqual(
        fire.Fire(tc.Underscores, 'underscore-function example'), 'example')
    self.assertEqual(
        fire.Fire(tc.Underscores, 'underscore_function --underscore-arg=score'),
        'score')
    self.assertEqual(
        fire.Fire(tc.Underscores, 'underscore_function --underscore_arg=score'),
        'score')

  def testBoolParsing(self):
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool True'), True)
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool False'), False)
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool --arg=True'), True)
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool --arg=False'), False)
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool --arg'), True)
    self.assertEqual(fire.Fire(tc.BoolConverter, 'as-bool --noarg'), False)

  def testBoolParsingContinued(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity True False'), (True, False))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha=False 10'), (False, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha --beta 10'), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha --beta=10'), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --noalpha --beta'), (False, True))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity 10 --beta'), (10, True))

  def testBoolParsingLessExpectedCases(self):
    # Note: Does not return (True, 10).
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha 10'), (10, '0'))
    # To get (True, 10), use one of the following:
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity --alpha --beta=10'), (True, 10))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity True 10'), (True, 10))

    # Note: Does not return ('--test', '0').
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity --alpha --test'),
                     (True, '--test'))
    # To get ('--test', '0'), use one of the following:
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity --alpha=--test'),
                     ('--test', '0'))
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, r'identity --alpha \"--test\"'),
        ('--test', '0'))

  def testBoolParsingWithNo(self):
    # In these examples --nothing always refers to the nothing argument:
    def fn1(thing, nothing):
      return thing, nothing

    self.assertEqual(fire.Fire(fn1, '--thing --nothing'), (True, True))
    self.assertEqual(fire.Fire(fn1, '--thing --nonothing'), (True, False))

    with self.assertRaisesFireExit(2):
      # In this case nothing=False (since rightmost setting of a flag gets
      # precedence), but it errors because thing has no value.
      fire.Fire(fn1, '--nothing --nonothing')

    # In these examples, --nothing sets thing=False:
    def fn2(thing, **kwargs):
      return thing, kwargs
    self.assertEqual(fire.Fire(fn2, '--thing'), (True, {}))
    self.assertEqual(fire.Fire(fn2, '--nothing'), (False, {}))
    with self.assertRaisesFireExit(2):
      # In this case, nothing=True, but it errors because thing has no value.
      fire.Fire(fn2, '--nothing=True')
    self.assertEqual(fire.Fire(fn2, '--nothing --nothing=True'),
                     (False, {'nothing': True}))

    def fn3(arg, **kwargs):
      return arg, kwargs
    self.assertEqual(fire.Fire(fn3, '--arg=value --thing'),
                     ('value', {'thing': True}))
    self.assertEqual(fire.Fire(fn3, '--arg=value --nothing'),
                     ('value', {'thing': False}))
    self.assertEqual(fire.Fire(fn3, '--arg=value --nonothing'),
                     ('value', {'nothing': False}))

  def testTraceFlag(self):
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, 'as-bool True -- --trace')
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, 'as-bool True -- -t')
    with self.assertRaisesFireExit(0, 'Fire trace:\n'):
      fire.Fire(tc.BoolConverter, '-- --trace')

  def testHelpFlag(self):
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, 'as-bool True -- --help')
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, 'as-bool True -- -h')
    with self.assertRaisesFireExit(0):
      fire.Fire(tc.BoolConverter, '-- --help')

  def testHelpFlagAndTraceFlag(self):
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*Usage:'):
      fire.Fire(tc.BoolConverter, 'as-bool True -- --help --trace')
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*Usage:'):
      fire.Fire(tc.BoolConverter, 'as-bool True -- -h -t')
    with self.assertRaisesFireExit(0, 'Fire trace:\n.*Usage:'):
      fire.Fire(tc.BoolConverter, '-- -h --trace')

  def testTabCompletionNoName(self):
    completion_script = fire.Fire(tc.NoDefaults, '-- --completion')
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletion(self):
    completion_script = fire.Fire(tc.NoDefaults, '-- --completion', name='c')
    self.assertIn('double', completion_script)
    self.assertIn('triple', completion_script)

  def testTabCompletionWithDict(self):
    actions = {'multiply': lambda a, b: a * b}
    completion_script = fire.Fire(actions, '-- --completion', name='actCLI')
    self.assertIn('actCLI', completion_script)
    self.assertIn('multiply', completion_script)

  def testBasicSeparator(self):
    # '-' is the default separator.
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity + _'), ('+', '_'))
    self.assertEqual(fire.Fire(tc.MixedDefaults, 'identity _ + -'), ('_', '+'))

    # If we change the separator we can use '-' as an argument.
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'identity - _ -- --separator &'),
        ('-', '_'))

    # The separator triggers a function call, but there aren't enough arguments.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.MixedDefaults, 'identity - _ +')

  def testNonComparable(self):
    """Fire should work with classes that disallow comparisons."""
    self.assertIsInstance(fire.Fire(tc.NonComparable, ''), tc.NonComparable)

    # The first separator instantiates the NonComparable object.
    # The second separator causes Fire to check if the separator was necessary.
    self.assertIsInstance(fire.Fire(tc.NonComparable, '- -'), tc.NonComparable)

  def testExtraSeparators(self):
    self.assertEqual(
        fire.Fire(tc.ReturnsObj, 'get-obj arg1 arg2 - - as-bool True'), True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj, 'get-obj arg1 arg2 - - - as-bool True'), True)

  def testSeparatorForChaining(self):
    # Without a separator all args are consumed by get_obj.
    self.assertIsInstance(
        fire.Fire(tc.ReturnsObj, 'get-obj arg1 arg2 as-bool True'),
        tc.BoolConverter)
    # With a separator only the preceeding args are consumed by get_obj.
    self.assertEqual(
        fire.Fire(tc.ReturnsObj, 'get-obj arg1 arg2 - as-bool True'), True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  'get-obj arg1 arg2 & as-bool True -- --separator &'),
        True)
    self.assertEqual(
        fire.Fire(tc.ReturnsObj,
                  'get-obj arg1 $$ as-bool True -- --separator $$'),
        True)

  def testFloatForExpectedInt(self):
    self.assertEqual(
        fire.Fire(tc.MixedDefaults, 'sum --alpha 2.2 --beta 3.0'), 8.2)
    self.assertEqual(
        fire.Fire(tc.NumberDefaults, 'integer_reciprocal --divisor 5.0'), 0.2)
    self.assertEqual(
        fire.Fire(tc.NumberDefaults, 'integer_reciprocal 4.0'), 0.25)

  def testClassInstantiation(self):
    self.assertIsInstance(fire.Fire(tc.InstanceVars, '--arg1=a1 --arg2=a2'),
                          tc.InstanceVars)
    with self.assertRaisesFireExit(2):
      # Cannot instantiate a class with positional args.
      fire.Fire(tc.InstanceVars, 'a1 a2')

  def testTraceErrors(self):
    # Class needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, 'a1')
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, '--arg1=a1')

    # Routine needs additional value but runs out of args.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, 'a1 a2 - run b1')
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, '--arg1=a1 --arg2=a2 - run b1')

    # Extra args cannot be consumed.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, 'a1 a2 - run b1 b2 b3')
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, '--arg1=a1 --arg2=a2 - run b1 b2 b3')

    # Cannot find member to access.
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, 'a1 a2 - jog')
    with self.assertRaisesFireExit(2):
      fire.Fire(tc.InstanceVars, '--arg1=a1 --arg2=a2 - jog')


if __name__ == '__main__':
  testutils.main()
