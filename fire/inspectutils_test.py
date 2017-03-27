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

"""Tests for the inspectutils module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

from fire import inspectutils
from fire import test_components as tc
from fire import testutils

import six


class InspectUtilsTest(testutils.BaseTestCase):

  def testGetFullArgSpec(self):
    spec = inspectutils.GetFullArgSpec(tc.identity)
    self.assertEqual(spec.args, ['arg1', 'arg2', 'arg3', 'arg4'])
    self.assertEqual(spec.defaults, (10, 20))
    self.assertEqual(spec.varargs, 'arg5')
    self.assertEqual(spec.varkw, 'arg6')
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {'arg2': int, 'arg4': int})

  @unittest.skipIf(six.PY2, 'No keyword arguments in python 2')
  def testGetFullArgSpecPy3(self):
    spec = inspectutils.GetFullArgSpec(tc.py3.identity)
    self.assertEqual(spec.args, ['arg1', 'arg2', 'arg3', 'arg4'])
    self.assertEqual(spec.defaults, (10, 20))
    self.assertEqual(spec.varargs, 'arg5')
    self.assertEqual(spec.varkw, 'arg10')
    self.assertEqual(spec.kwonlyargs, ['arg6', 'arg7', 'arg8', 'arg9'])
    self.assertEqual(spec.kwonlydefaults, {'arg8': 30, 'arg9': 40})
    self.assertEqual(spec.annotations,
                     {'arg2': int, 'arg4': int, 'arg7': int, 'arg9': int})

  def testGetFullArgSpecFromBuiltin(self):
    spec = inspectutils.GetFullArgSpec('test'.upper)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, 'vars')
    self.assertEqual(spec.varkw, 'kwargs')
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromSlotWrapper(self):
    spec = inspectutils.GetFullArgSpec(tc.NoDefaults)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromClassNoInit(self):
    spec = inspectutils.GetFullArgSpec(tc.OldStyleEmpty)
    self.assertEqual(spec.args, [])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testGetFullArgSpecFromMethod(self):
    spec = inspectutils.GetFullArgSpec(tc.NoDefaults().double)
    self.assertEqual(spec.args, ['count'])
    self.assertEqual(spec.defaults, ())
    self.assertEqual(spec.varargs, None)
    self.assertEqual(spec.varkw, None)
    self.assertEqual(spec.kwonlyargs, [])
    self.assertEqual(spec.kwonlydefaults, {})
    self.assertEqual(spec.annotations, {})

  def testInfoOne(self):
    info = inspectutils.Info(1)
    self.assertEqual(info.get('type_name'), 'int')
    self.assertEqual(info.get('file'), None)
    self.assertEqual(info.get('line'), None)
    self.assertEqual(info.get('string_form'), '1')

  def testInfoClass(self):
    info = inspectutils.Info(tc.NoDefaults)
    self.assertEqual(info.get('type_name'), 'type')
    self.assertIn(os.path.join('fire', 'test_components.py'), info.get('file'))
    self.assertGreater(info.get('line'), 0)

  def testInfoClassNoInit(self):
    info = inspectutils.Info(tc.OldStyleEmpty)
    if six.PY2:
      self.assertEqual(info.get('type_name'), 'classobj')
    else:
      self.assertEqual(info.get('type_name'), 'type')
    self.assertIn(os.path.join('fire', 'test_components.py'), info.get('file'))
    self.assertGreater(info.get('line'), 0)


if __name__ == '__main__':
  testutils.main()
