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

from fire import inspectutils
from fire import test_components as tc
import six

import unittest


class InspectUtilsTest(unittest.TestCase):

  def testGetArgSpecReturnType(self):
    # Asserts that the named tuple returned by GetArgSpec has the appropriate
    # fields.
    spec = inspectutils.GetArgSpec(tc.identity)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(spec.args, args)
    self.assertEqual(spec.defaults, defaults)
    self.assertEqual(spec.varargs, varargs)
    self.assertEqual(spec.varkw, varkw)
    self.assertEqual(spec.kwonlyargs, kwonly)
    self.assertEqual(spec.kwonlydefaults, kwonlydefaults)
    self.assertEqual(spec.annotations, annotations)

  def testGetArgSpec(self):
    spec = inspectutils.GetArgSpec(tc.identity)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(args, ['arg1', 'arg2', 'arg3', 'arg4'])
    self.assertEqual(defaults, (10, 20))
    self.assertEqual(varargs, 'arg5')
    self.assertEqual(varkw, 'arg10')
    if six.PY2:
      self.assertEqual(kwonly, [])
      self.assertEqual(kwonlydefaults, {})
      self.assertEqual(annotations, {'arg2': int, 'arg4': int})
    else:
      self.assertEqual(kwonly, ['arg6', 'arg7', 'arg8', 'arg9'])
      self.assertEqual(kwonlydefaults, {'arg8': 30, 'arg9': 40})
      self.assertEqual(annotations,
        {'arg2': int, 'arg4': int, 'arg7': int, 'arg9': int})

  def testGetArgSpecBuiltin(self):
    spec = inspectutils.GetArgSpec('test'.upper)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, 'vars')
    self.assertEqual(varkw, 'kwargs')
    self.assertEqual(kwonly, [])
    self.assertEqual(kwonlydefaults, {})
    self.assertEqual(annotations, {})

  def testGetArgSpecSlotWrapper(self):
    spec = inspectutils.GetArgSpec(tc.NoDefaults)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(varkw, None)
    self.assertEqual(kwonly, [])
    self.assertEqual(kwonlydefaults, {})
    self.assertEqual(annotations, {})

  def testGetArgSpecClassNoInit(self):
    spec = inspectutils.GetArgSpec(tc.OldStyleEmpty)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(varkw, None)
    self.assertEqual(kwonly, [])
    self.assertEqual(kwonlydefaults, {})
    self.assertEqual(annotations, {})

  def testGetArgSpecMethod(self):
    spec = inspectutils.GetArgSpec(tc.NoDefaults().double)
    args, varargs, varkw, defaults, kwonly, kwonlydefaults, annotations = spec

    self.assertEqual(args, ['count'])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(varkw, None)
    self.assertEqual(kwonly, [])
    self.assertEqual(kwonlydefaults, {})
    self.assertEqual(annotations, {})

  def testInfoOne(self):
    info = inspectutils.Info(1)
    self.assertEqual(info.get('type_name'), 'int')
    self.assertEqual(info.get('file'), None)
    self.assertEqual(info.get('line'), None)
    self.assertEqual(info.get('string_form'), '1')

  def testInfoClass(self):
    info = inspectutils.Info(tc.NoDefaults)
    self.assertEqual(info.get('type_name'), 'type')
    self.assertIn('fire/test_components.py', info.get('file'))
    self.assertGreater(info.get('line'), 0)

  def testInfoClassNoInit(self):
    info = inspectutils.Info(tc.OldStyleEmpty)
    if six.PY2:
      self.assertEqual(info.get('type_name'), 'classobj')
    else:
      self.assertEqual(info.get('type_name'), 'type')
    self.assertIn('fire/test_components.py', info.get('file'))
    self.assertGreater(info.get('line'), 0)


if __name__ == '__main__':
  unittest.main()
