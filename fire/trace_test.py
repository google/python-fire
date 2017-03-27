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

"""Tests for the trace module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import testutils
from fire import trace


class FireTraceTest(testutils.BaseTestCase):

  def testFireTraceInitialization(self):
    t = trace.FireTrace(10)
    self.assertIsNotNone(t)
    self.assertIsNotNone(t.elements)

  def testFireTraceGetResult(self):
    t = trace.FireTrace('start')
    self.assertEqual(t.GetResult(), 'start')
    t.AddAccessedProperty('t', 'final', None, 'example.py', 10)
    self.assertEqual(t.GetResult(), 't')

  def testFireTraceHasError(self):
    t = trace.FireTrace('start')
    self.assertFalse(t.HasError())
    t.AddAccessedProperty('t', 'final', None, 'example.py', 10)
    self.assertFalse(t.HasError())
    t.AddError(ValueError('example error'), ['arg'])
    self.assertTrue(t.HasError())

  def testAddAccessedProperty(self):
    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddAccessedProperty('new component', 'prop', args, 'sample.py', 12)
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Accessed property "prop" (sample.py:12)')

  def testAddCalledRoutine(self):
    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledRoutine('result', 'run', args, 'sample.py', 12, False)
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Called routine "run" (sample.py:12)')

  def testAddInstantiatedClass(self):
    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddInstantiatedClass(
        'Classname', 'classname', args, 'sample.py', 12, False)
    target = """1. Initial component
2. Instantiated class "classname" (sample.py:12)"""
    self.assertEqual(str(t), target)

  def testAddCompletionScript(self):
    t = trace.FireTrace('initial object')
    t.AddCompletionScript('This is the completion script string.')
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Generated completion script')

  def testAddInteractiveMode(self):
    t = trace.FireTrace('initial object')
    t.AddInteractiveMode()
    self.assertEqual(
        str(t),
        '1. Initial component\n2. Entered interactive mode')

  def testGetCommand(self):
    t = trace.FireTrace('initial object')
    args = ('example', 'args')
    t.AddCalledRoutine('result', 'run', args, 'sample.py', 12, False)
    self.assertEqual(t.GetCommand(), 'example args')

  def testGetCommandWithQuotes(self):
    t = trace.FireTrace('initial object')
    args = ('example', 'spaced arg')
    t.AddCalledRoutine('result', 'run', args, 'sample.py', 12, False)
    self.assertEqual(t.GetCommand(), "example 'spaced arg'")

  def testGetCommandWithFlagQuotes(self):
    t = trace.FireTrace('initial object')
    args = ('--example=spaced arg',)
    t.AddCalledRoutine('result', 'run', args, 'sample.py', 12, False)
    self.assertEqual(t.GetCommand(), "--example='spaced arg'")


class FireTraceElementTest(testutils.BaseTestCase):

  def testFireTraceElementHasError(self):
    el = trace.FireTraceElement()
    self.assertFalse(el.HasError())

    el = trace.FireTraceElement(error=ValueError('example error'))
    self.assertTrue(el.HasError())

  def testFireTraceElementAsStringNoMetadata(self):
    el = trace.FireTraceElement(
        component='Example',
        action='Fake action',
    )
    self.assertEqual(str(el), 'Fake action')

  def testFireTraceElementAsStringWithTarget(self):
    el = trace.FireTraceElement(
        component='Example',
        action='Created toy',
        target='Beaker',
    )
    self.assertEqual(str(el), 'Created toy "Beaker"')

  def testFireTraceElementAsStringWithTargetAndLineNo(self):
    el = trace.FireTraceElement(
        component='Example',
        action='Created toy',
        target='Beaker',
        filename='beaker.py',
        lineno=10,
    )
    self.assertEqual(str(el), 'Created toy "Beaker" (beaker.py:10)')


if __name__ == '__main__':
  testutils.main()
