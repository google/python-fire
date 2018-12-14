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

"""Tests for the helputils module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import textwrap

from fire import helputils
from fire import test_components as tc
from fire import testutils
from fire import trace
import six


class HelpUtilsTest(testutils.BaseTestCase):

  def testHelpStringClass(self):
    helpstring = helputils.HelpString(tc.NoDefaults)
    self.assertIn('Type:        type', helpstring)
    self.assertIn("String form: <class 'fire.test_components.NoDefaults'>",
                  helpstring)
    self.assertIn('test_components.py', helpstring)
    self.assertIn('Line:        ', helpstring)
    self.assertNotIn('Usage', helpstring)

  def testHelpStringObject(self):
    obj = tc.NoDefaults()
    helpstring = helputils.HelpString(obj)
    self.assertIn('Type:        NoDefaults', helpstring)
    self.assertIn('String form: <fire.test_components.NoDefaults object at ',
                  helpstring)
    # TODO(dbieber): We comment this out since it only works with IPython:
    # self.assertIn('test_components.py', helpstring)
    self.assertIn('Usage:       double\n'
                  '             triple', helpstring)

  def testHelpStringFunction(self):
    obj = tc.NoDefaults()
    helpstring = helputils.HelpString(obj.double)
    if six.PY2:
      self.assertIn('Type:        instancemethod\n', helpstring)
    else:
      self.assertIn('Type:        method\n', helpstring)
    self.assertIn(
        'String form: <bound method NoDefaults.double of '
        '<fire.test_components.NoDefaults object',
        helpstring)
    self.assertIn('test_components.py', helpstring)
    self.assertIn('Line:        ', helpstring)
    self.assertIn('Usage:       COUNT\n'
                  '             --count COUNT', helpstring)

  def testHelpStringFunctionWithDefaults(self):
    obj = tc.WithDefaults()
    helpstring = helputils.HelpString(obj.triple)
    if six.PY2:
      self.assertIn('Type:        instancemethod\n', helpstring)
    else:
      self.assertIn('Type:        method\n', helpstring)
    self.assertIn(
        'String form: <bound method WithDefaults.triple of '
        '<fire.test_components.WithDefaults object',
        helpstring)
    self.assertIn('test_components.py', helpstring)
    self.assertIn('Line:        ', helpstring)
    self.assertIn('Usage:       [COUNT]\n'
                  '             [--count COUNT]', helpstring)

  def testHelpStringBuiltin(self):
    helpstring = helputils.HelpString('test'.upper)
    self.assertIn('Type:        builtin_function_or_method', helpstring)
    self.assertIn('String form: <built-in method upper of', helpstring)
    self.assertIn('Usage:       [VARS ...] [--KWARGS ...]', helpstring)

  def testHelpStringIntType(self):
    helpstring = helputils.HelpString(int)
    self.assertIn('Type:        type', helpstring)
    if six.PY2:
      self.assertIn("String form: <type 'int'>", helpstring)
    else:
      self.assertIn("String form: <class 'int'>", helpstring)
    self.assertNotIn('Usage', helpstring)

  def testHelpStringEmptyList(self):
    helpstring = helputils.HelpString([])
    self.assertIn('Type:        list', helpstring)
    self.assertIn('String form: []', helpstring)
    self.assertIn('Length:      0', helpstring)

  def testHelpStringShortList(self):
    helpstring = helputils.HelpString([10])
    self.assertIn('Type:        list', helpstring)
    self.assertIn('String form: [10]', helpstring)
    self.assertIn('Length:      1', helpstring)
    self.assertIn('Usage:       [0]', helpstring)  # [] denotes optional.

  def testHelpStringInt(self):
    helpstring = helputils.HelpString(7)
    self.assertIn('Type:        int', helpstring)
    self.assertIn('String form: 7', helpstring)
    self.assertIn('Usage:       bit-length\n'
                  '             conjugate\n'
                  '             denominator\n', helpstring)

  def testHelpClassNoInit(self):
    helpstring = helputils.HelpString(tc.OldStyleEmpty)
    if six.PY2:
      self.assertIn('Type:        classobj\n', helpstring)
    else:
      self.assertIn('Type:        type\n', helpstring)
    self.assertIn('String form: ', helpstring)
    self.assertIn('fire.test_components.OldStyleEmpty', helpstring)
    self.assertIn(os.path.join('fire', 'test_components.py'), helpstring)
    self.assertIn('Line:        ', helpstring)


class UsageTest(testutils.BaseTestCase):

  def testUsageOutput(self):
    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helputils.UsageText(component, trace=t, verbose=False)
    expected_output = '''
    Usage: NoDefaults <commands>
    available commands: double | triple

    For detailed information on this command, run:
    NoDefaults --help
    '''

    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputVerbose(self):
    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    expected_output = '''
    Usage: NoDefaults <commands>
    available commands: double | triple

    For detailed information on this command, run:
    NoDefaults --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputMethod(self):
    component = tc.NoDefaults().double
    t = trace.FireTrace(component, name='NoDefaults')
    t.AddAccessedProperty(component, 'double', ['double'], None, None)
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    expected_output = '''
    Usage: NoDefaults double COUNT

    For detailed information on this command, run:
    NoDefaults double --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithHelp(self):
    component = tc.function_with_help
    t = trace.FireTrace(component, name='function_with_help')
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    expected_output = '''
    Usage: function_with_help <flags>

    Available flags: --help

    For detailed information on this command, run:
    function_with_help -- --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithDocstring(self):
    component = tc.multiplier_with_docstring
    t = trace.FireTrace(component, name='multiplier_with_docstring')
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    expected_output = '''
    Usage: multiplier_with_docstring NUM <flags>

    Available flags: --rate

    For detailed information on this command, run:
    multiplier_with_docstring --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  @testutils.skip('The functionality is not implemented yet')
  def testUsageOutputCallable(self):
    # This is both a group and a command!
    component = tc.CallableWithKeywordArgument
    t = trace.FireTrace(component, name='CallableWithKeywordArgument')
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    # TODO(zuhaohen): We need to handle the case for keyword args as well
    # i.e. __call__ method of CallableWithKeywordArgument
    expected_output = '''
    Usage: CallableWithKeywordArgument <commands>

    Available commands: print_msg

    For detailed information on this command, run:
    CallableWithKeywordArgument -- --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputConstructorWithParameter(self):
    component = tc.InstanceVars
    t = trace.FireTrace(component, name='InstanceVars')
    usage_output = helputils.UsageText(component, trace=t, verbose=True)
    expected_output = '''
    Usage: InstanceVars ARG1 ARG2

    For detailed information on this command, run:
    InstanceVars --help
    '''
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

if __name__ == '__main__':
  testutils.main()
