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

"""Tests for the decorators module."""

from fire import core
from fire import decorators
from fire import testutils


class NoDefaults:
  """A class for testing decorated functions without default values."""

  @decorators.SetParseFns(count=int)
  def double(self, count):
    return 2 * count

  @decorators.SetParseFns(count=float)
  def triple(self, count):
    return 3 * count

  @decorators.SetParseFns(int)
  def quadruple(self, count):
    return 4 * count


@decorators.SetParseFns(int)
def double(count):
  return 2 * count


class WithDefaults:

  @decorators.SetParseFns(float)
  def example1(self, arg1=10):
    return arg1, type(arg1)

  @decorators.SetParseFns(arg1=float)
  def example2(self, arg1=10):
    return arg1, type(arg1)


class MixedArguments:

  @decorators.SetParseFns(float, arg2=str)
  def example3(self, arg1, arg2):
    return arg1, arg2


class PartialParseFn:

  @decorators.SetParseFns(arg1=str)
  def example4(self, arg1, arg2):
    return arg1, arg2

  @decorators.SetParseFns(arg2=str)
  def example5(self, arg1, arg2):
    return arg1, arg2


class WithKwargs:

  @decorators.SetParseFns(mode=str, count=int)
  def example6(self, **kwargs):
    return (
        kwargs.get('mode', 'default'),
        kwargs.get('count', 0),
    )


class WithVarArgs:

  @decorators.SetParseFn(str)
  def example7(self, arg1, arg2=None, *varargs, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    return arg1, arg2, varargs, kwargs


class FireDecoratorsTest(testutils.BaseTestCase):

  def testSetParseFnsNamedArgs(self):
    self.assertEqual(core.Fire(NoDefaults, command=['double', '2']), 4)
    self.assertEqual(core.Fire(NoDefaults, command=['triple', '4']), 12.0)

  def testSetParseFnsPositionalArgs(self):
    self.assertEqual(core.Fire(NoDefaults, command=['quadruple', '5']), 20)

  def testSetParseFnsFnWithPositionalArgs(self):
    self.assertEqual(core.Fire(double, command=['5']), 10)

  def testSetParseFnsDefaultsFromPython(self):
    # When called from Python, function should behave normally.
    self.assertTupleEqual(WithDefaults().example1(), (10, int))
    self.assertEqual(WithDefaults().example1(5), (5, int))
    self.assertEqual(WithDefaults().example1(12.0), (12, float))

  def testSetParseFnsDefaultsFromFire(self):
    # Fire should use the decorator to know how to parse string arguments.
    self.assertEqual(core.Fire(WithDefaults, command=['example1']), (10, int))
    self.assertEqual(core.Fire(WithDefaults, command=['example1', '10']),
                     (10, float))
    self.assertEqual(core.Fire(WithDefaults, command=['example1', '13']),
                     (13, float))
    self.assertEqual(core.Fire(WithDefaults, command=['example1', '14.0']),
                     (14, float))

  def testSetParseFnsNamedDefaultsFromPython(self):
    # When called from Python, function should behave normally.
    self.assertTupleEqual(WithDefaults().example2(), (10, int))
    self.assertEqual(WithDefaults().example2(5), (5, int))
    self.assertEqual(WithDefaults().example2(12.0), (12, float))

  def testSetParseFnsNamedDefaultsFromFire(self):
    # Fire should use the decorator to know how to parse string arguments.
    self.assertEqual(core.Fire(WithDefaults, command=['example2']), (10, int))
    self.assertEqual(core.Fire(WithDefaults, command=['example2', '10']),
                     (10, float))
    self.assertEqual(core.Fire(WithDefaults, command=['example2', '13']),
                     (13, float))
    self.assertEqual(core.Fire(WithDefaults, command=['example2', '14.0']),
                     (14, float))

  def testSetParseFnsPositionalAndNamed(self):
    self.assertEqual(core.Fire(MixedArguments, ['example3', '10', '10']),
                     (10, '10'))

  def testSetParseFnsOnlySomeTypes(self):
    self.assertEqual(
        core.Fire(PartialParseFn, command=['example4', '10', '10']), ('10', 10))
    self.assertEqual(
        core.Fire(PartialParseFn, command=['example5', '10', '10']), (10, '10'))

  def testSetParseFnsForKeywordArgs(self):
    self.assertEqual(
        core.Fire(WithKwargs, command=['example6']), ('default', 0))
    self.assertEqual(
        core.Fire(WithKwargs, command=['example6', '--herring', '"red"']),
        ('default', 0))
    self.assertEqual(
        core.Fire(WithKwargs, command=['example6', '--mode', 'train']),
        ('train', 0))
    self.assertEqual(core.Fire(WithKwargs, command=['example6', '--mode', '3']),
                     ('3', 0))
    self.assertEqual(
        core.Fire(WithKwargs,
                  command=['example6', '--mode', '-1', '--count', '10']),
        ('-1', 10))
    self.assertEqual(
        core.Fire(WithKwargs, command=['example6', '--count', '-2']),
        ('default', -2))

  def testSetParseFn(self):
    self.assertEqual(
        core.Fire(WithVarArgs,
                  command=['example7', '1', '--arg2=2', '3', '4', '--kwarg=5']),
        ('1', '2', ('3', '4'), {'kwarg': '5'}))


if __name__ == '__main__':
  testutils.main()
