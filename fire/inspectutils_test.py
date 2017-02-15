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
    argspec = inspectutils.GetArgSpec(tc.identity)
    args, varargs, keywords, defaults = argspec
    self.assertEqual(argspec.args, args)
    self.assertEqual(argspec.defaults, defaults)
    self.assertEqual(argspec.varargs, varargs)
    self.assertEqual(argspec.keywords, keywords)

  def testGetArgSpec(self):
    args, varargs, keywords, defaults = inspectutils.GetArgSpec(tc.identity)
    self.assertEqual(args, ['arg1', 'arg2'])
    self.assertEqual(defaults, (10,))
    self.assertEqual(varargs, 'arg3')
    self.assertEqual(keywords, 'arg4')

  def testGetArgSpecBuiltin(self):
    args, varargs, keywords, defaults = inspectutils.GetArgSpec('test'.upper)
    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, 'vars')
    self.assertEqual(keywords, 'kwargs')

  def testGetArgSpecSlotWrapper(self):
    args, varargs, keywords, defaults = inspectutils.GetArgSpec(tc.NoDefaults)
    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(keywords, None)

  def testGetArgSpecClassNoInit(self):
    args, varargs, keywords, defaults = inspectutils.GetArgSpec(
        tc.OldStyleEmpty)
    self.assertEqual(args, [])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(keywords, None)

  def testGetArgSpecMethod(self):
    args, varargs, keywords, defaults = inspectutils.GetArgSpec(
        tc.NoDefaults().double)
    self.assertEqual(args, ['count'])
    self.assertEqual(defaults, ())
    self.assertEqual(varargs, None)
    self.assertEqual(keywords, None)

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
