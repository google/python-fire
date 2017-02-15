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
from fire import decorators

import unittest


class A(object):

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


class B(object):

  @decorators.SetParseFns(float)
  def example1(self, arg1=10):
    return arg1, type(arg1)

  @decorators.SetParseFns(arg1=float)
  def example2(self, arg1=10):
    return arg1, type(arg1)


class C(object):

  @decorators.SetParseFns(float, arg2=str)
  def example3(self, arg1, arg2):
    return arg1, arg2


class D(object):

  @decorators.SetParseFns(arg1=str)
  def example4(self, arg1, arg2):
    return arg1, arg2

  @decorators.SetParseFns(arg2=str)
  def example5(self, arg1, arg2):
    return arg1, arg2


class E(object):

  @decorators.SetParseFns(mode=str, count=int)
  def example6(self, **kwargs):
    return (
        kwargs.get('mode', 'default'),
        kwargs.get('count', 0),
    )


class F(object):

  @decorators.SetParseFn(str)
  def example7(self, arg1, arg2=None, *varargs, **kwargs):
    return arg1, arg2, varargs, kwargs


class FireDecoratorsTest(unittest.TestCase):

  def testSetParseFnsNamedArgs(self):
    self.assertEqual(core.Fire(A, 'double 2'), 4)
    self.assertEqual(core.Fire(A, 'triple 4'), 12.0)

  def testSetParseFnsPositionalArgs(self):
    self.assertEqual(core.Fire(A, 'quadruple 5'), 20)

  def testSetParseFnsFnWithPositionalArgs(self):
    self.assertEqual(core.Fire(double, '5'), 10)

  def testSetParseFnsDefaultsFromPython(self):
    # When called from Python, function should behave normally.
    self.assertTupleEqual(B().example1(), (10, int))
    self.assertEqual(B().example1(5), (5, int))
    self.assertEqual(B().example1(12.0), (12, float))

  def testSetParseFnsDefaultsFromFire(self):
    # Fire should use the decorator to know how to parse string arguments.
    self.assertEqual(core.Fire(B, 'example1'), (10, int))
    self.assertEqual(core.Fire(B, 'example1 10'), (10, float))
    self.assertEqual(core.Fire(B, 'example1 13'), (13, float))
    self.assertEqual(core.Fire(B, 'example1 14.0'), (14, float))

  def testSetParseFnsNamedDefaultsFromPython(self):
    # When called from Python, function should behave normally.
    self.assertTupleEqual(B().example2(), (10, int))
    self.assertEqual(B().example2(5), (5, int))
    self.assertEqual(B().example2(12.0), (12, float))

  def testSetParseFnsNamedDefaultsFromFire(self):
    # Fire should use the decorator to know how to parse string arguments.
    self.assertEqual(core.Fire(B, 'example2'), (10, int))
    self.assertEqual(core.Fire(B, 'example2 10'), (10, float))
    self.assertEqual(core.Fire(B, 'example2 13'), (13, float))
    self.assertEqual(core.Fire(B, 'example2 14.0'), (14, float))

  def testSetParseFnsPositionalAndNamed(self):
    self.assertEqual(core.Fire(C, 'example3 10 10'), (10, '10'))

  def testSetParseFnsOnlySomeTypes(self):
    self.assertEqual(core.Fire(D, 'example4 10 10'), ('10', 10))
    self.assertEqual(core.Fire(D, 'example5 10 10'), (10, '10'))

  def testSetParseFnsForKeywordArgs(self):
    self.assertEqual(core.Fire(E, 'example6'), ('default', 0))
    self.assertEqual(core.Fire(E, 'example6 --herring "red"'), ('default', 0))
    self.assertEqual(core.Fire(E, 'example6 --mode train'), ('train', 0))
    self.assertEqual(core.Fire(E, 'example6 --mode 3'), ('3', 0))
    self.assertEqual(core.Fire(E, 'example6 --mode -1 --count 10'), ('-1', 10))
    self.assertEqual(core.Fire(E, 'example6 --count -2'), ('default', -2))

  def testSetParseFn(self):
    self.assertEqual(core.Fire(F, 'example7 1 --arg2=2 3 4 --kwarg=5'),
                     ('1', '2', ('3', '4'), {'kwarg': '5'}))


if __name__ == '__main__':
  unittest.main()
