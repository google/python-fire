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

"""Tests for the helptext module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import textwrap

from fire import formatting
from fire import helptext
from fire import test_components as tc
from fire import testutils
from fire import trace
import six


class HelpTest(testutils.BaseTestCase):

  def setUp(self):
    super(HelpTest, self).setUp()
    os.environ['ANSI_COLORS_DISABLED'] = '1'

  def testHelpTextNoDefaults(self):
    component = tc.NoDefaults
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='NoDefaults'))
    self.assertIn('NAME\n    NoDefaults', help_screen)
    self.assertIn('SYNOPSIS\n    NoDefaults', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextNoDefaultsObject(self):
    component = tc.NoDefaults()
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='NoDefaults'))
    self.assertIn('NAME\n    NoDefaults', help_screen)
    self.assertIn('SYNOPSIS\n    NoDefaults COMMAND', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('COMMANDS\n    COMMAND is one of the following:',
                  help_screen)
    self.assertIn('double', help_screen)
    self.assertIn('triple', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunction(self):
    component = tc.NoDefaults().double
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double COUNT', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('POSITIONAL ARGUMENTS\n    COUNT', help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  def testHelpTextFunctionWithDefaults(self):
    component = tc.WithDefaults().triple
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='triple'))
    self.assertIn('NAME\n    triple', help_screen)
    self.assertIn('SYNOPSIS\n    triple <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('FLAGS\n    --count=COUNT\n        Default: 0', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunctionWithLongDefaults(self):
    component = tc.WithDefaults().text
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='text'))
    self.assertIn('NAME\n    text', help_screen)
    self.assertIn('SYNOPSIS\n    text <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    --string=STRING\n'
        '        Default: \'0001020304050607080910'
        '1112131415161718192021222324252627282...',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithDefaultsAndTypes(self):
    component = tc.py3.WithDefaultsAndTypes().double
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double <flags>', help_screen)
    self.assertIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    --count=COUNT\n        Type: float\n        Default: 0',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithTypesAndDefaultNone(self):
    component = tc.py3.WithDefaultsAndTypes().get_int
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='get_int'))
    self.assertIn('NAME\n    get_int', help_screen)
    self.assertIn('SYNOPSIS\n    get_int <flags>', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn(
        'FLAGS\n    --value=VALUE\n'
        '        Type: Optional[int]\n        Default: None',
        help_screen)
    self.assertNotIn('NOTES', help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithTypes(self):
    component = tc.py3.WithTypes().double
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='double'))
    self.assertIn('NAME\n    double', help_screen)
    self.assertIn('SYNOPSIS\n    double COUNT', help_screen)
    self.assertIn('DESCRIPTION', help_screen)
    self.assertIn(
        'POSITIONAL ARGUMENTS\n    COUNT\n        Type: float',
        help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  @testutils.skipIf(
      sys.version_info[0:2] < (3, 5),
      'Python < 3.5 does not support type hints.')
  def testHelpTextFunctionWithLongTypes(self):
    component = tc.py3.WithTypes().long_type
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, name='long_type'))
    self.assertIn('NAME\n    long_type', help_screen)
    self.assertIn('SYNOPSIS\n    long_type LONG_OBJ', help_screen)
    self.assertNotIn('DESCRIPTION', help_screen)
    # TODO(dbieber): Assert type is displayed correctly. Type displays
    # differently in Travis vs in Google.
    # self.assertIn(
    #     'POSITIONAL ARGUMENTS\n    LONG_OBJ\n'
    #     '        Type: typing.Tuple[typing.Tuple['
    #     'typing.Tuple[typing.Tuple[typing.Tupl...',
    #     help_screen)
    self.assertIn(
        'NOTES\n    You can also use flags syntax for POSITIONAL ARGUMENTS',
        help_screen)

  def testHelpTextFunctionWithBuiltin(self):
    component = 'test'.upper
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'upper'))
    self.assertIn('NAME\n    upper', help_screen)
    self.assertIn('SYNOPSIS\n    upper', help_screen)
    # We don't check description content here since the content is python
    # version dependent.
    self.assertIn('DESCRIPTION\n', help_screen)
    self.assertNotIn('NOTES', help_screen)

  def testHelpTextFunctionIntType(self):
    component = int
    help_screen = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'int'))
    self.assertIn('NAME\n    int', help_screen)
    self.assertIn('SYNOPSIS\n    int', help_screen)
    # We don't check description content here since the content is python
    # version dependent.
    self.assertIn('DESCRIPTION\n', help_screen)

  def testHelpTextEmptyList(self):
    component = []
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'list'))
    self.assertIn('NAME\n    list', help_screen)
    self.assertIn('SYNOPSIS\n    list COMMAND', help_screen)
    # TODO(zuhaochen): Change assertion after custom description is
    # implemented for list type.
    self.assertNotIn('DESCRIPTION', help_screen)
    # We don't check the listed commands either since the list API could
    # potentially change between Python versions.
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)

  def testHelpTextShortList(self):
    component = [10]
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'list'))
    self.assertIn('NAME\n    list', help_screen)
    self.assertIn('SYNOPSIS\n    list COMMAND', help_screen)
    # TODO(zuhaochen): Change assertion after custom description is
    # implemented for list type.
    self.assertNotIn('DESCRIPTION', help_screen)

    # We don't check the listed commands comprehensively since the list API
    # could potentially change between Python versions. Check a few
    # functions(command) that we're confident likely remain available.
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)
    self.assertIn('     append\n', help_screen)

  def testHelpTextInt(self):
    component = 7
    help_screen = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, '7'))
    self.assertIn('NAME\n    7', help_screen)
    self.assertIn('SYNOPSIS\n    7 COMMAND | VALUE', help_screen)
    # TODO(zuhaochen): Change assertion after implementing custom
    # description for int.
    self.assertNotIn('DESCRIPTION', help_screen)
    self.assertIn('COMMANDS\n    COMMAND is one of the following:\n',
                  help_screen)
    self.assertIn('VALUES\n    VALUE is one of the following:\n', help_screen)

  def testHelpTextNoInit(self):
    component = tc.OldStyleEmpty
    help_screen = helptext.HelpText(
        component=component,
        trace=trace.FireTrace(component, 'OldStyleEmpty'))
    self.assertIn('NAME\n    OldStyleEmpty', help_screen)
    self.assertIn('SYNOPSIS\n    OldStyleEmpty', help_screen)

  @testutils.skipIf(
      six.PY2, 'Python 2 does not support keyword-only arguments.')
  def testHelpTextKeywordOnlyArgumentsWithDefault(self):
    component = tc.py3.KeywordOnly.with_default  # pytype: disable=module-attr
    output = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'with_default'))
    self.assertIn('NAME\n    with_default', output)
    self.assertIn('FLAGS\n    --x=X', output)

  @testutils.skipIf(
      six.PY2, 'Python 2 does not support keyword-only arguments.')
  def testHelpTextKeywordOnlyArgumentsWithoutDefault(self):
    component = tc.py3.KeywordOnly.double  # pytype: disable=module-attr
    output = helptext.HelpText(
        component=component, trace=trace.FireTrace(component, 'double'))
    self.assertIn('NAME\n    double', output)
    self.assertIn('FLAGS\n    --count=COUNT (required)', output)

  def testHelpScreen(self):
    component = tc.ClassWithDocstring()
    t = trace.FireTrace(component, name='ClassWithDocstring')
    help_output = helptext.HelpText(component, t)
    expected_output = """
NAME
    ClassWithDocstring - Test class for testing help text output.

SYNOPSIS
    ClassWithDocstring COMMAND | VALUE

DESCRIPTION
    This is some detail description of this test class.

COMMANDS
    COMMAND is one of the following:

     print_msg
       Prints a message.

VALUES
    VALUE is one of the following:

     message
       The default message to print."""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpScreenForFunctionDocstringWithLineBreak(self):
    component = tc.ClassWithMultilineDocstring.example_generator
    t = trace.FireTrace(component, name='example_generator')
    help_output = helptext.HelpText(component, t)
    expected_output = """
    NAME
        example_generator - Generators have a ``Yields`` section instead of a ``Returns`` section.

    SYNOPSIS
        example_generator N

    DESCRIPTION
        Generators have a ``Yields`` section instead of a ``Returns`` section.

    POSITIONAL ARGUMENTS
        N
            The upper limit of the range to generate, from 0 to `n` - 1.

    NOTES
        You can also use flags syntax for POSITIONAL ARGUMENTS"""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpScreenForFunctionFunctionWithDefaultArgs(self):
    component = tc.WithDefaults().double
    t = trace.FireTrace(component, name='double')
    help_output = helptext.HelpText(component, t)
    expected_output = """
    NAME
        double - Returns the input multiplied by 2.

    SYNOPSIS
        double <flags>

    DESCRIPTION
        Returns the input multiplied by 2.

    FLAGS
        --count=COUNT
            Default: 0
            Input number that you want to double."""
    self.assertEqual(textwrap.dedent(expected_output).strip(),
                     help_output.strip())

  def testHelpTextUnderlineFlag(self):
    component = tc.WithDefaults().triple
    t = trace.FireTrace(component, name='triple')
    help_screen = helptext.HelpText(component, t)
    self.assertIn(formatting.Bold('NAME') + '\n    triple', help_screen)
    self.assertIn(
        formatting.Bold('SYNOPSIS') + '\n    triple <flags>',
        help_screen)
    self.assertIn(
        formatting.Bold('FLAGS') + '\n    --' + formatting.Underline('count'),
        help_screen)

  def testHelpTextBoldCommandName(self):
    component = tc.ClassWithDocstring()
    t = trace.FireTrace(component, name='ClassWithDocstring')
    help_screen = helptext.HelpText(component, t)
    self.assertIn(
        formatting.Bold('NAME') + '\n    ClassWithDocstring', help_screen)
    self.assertIn(formatting.Bold('COMMANDS') + '\n', help_screen)
    self.assertIn(
        formatting.BoldUnderline('COMMAND') + ' is one of the following:\n',
        help_screen)
    self.assertIn(formatting.Bold('print_msg') + '\n', help_screen)

  def testHelpTextObjectWithGroupAndValues(self):
    component = tc.TypedProperties()
    t = trace.FireTrace(component, name='TypedProperties')
    help_screen = helptext.HelpText(
        component=component, trace=t, verbose=True)
    print(help_screen)
    self.assertIn('GROUPS', help_screen)
    self.assertIn('GROUP is one of the following:', help_screen)
    self.assertIn(
        'charlie\n       Class with functions that have default arguments.',
        help_screen)
    self.assertIn('VALUES', help_screen)
    self.assertIn('VALUE is one of the following:', help_screen)
    self.assertIn('alpha', help_screen)

  def testHelpTextNameSectionCommandWithSeparator(self):
    component = 9
    t = trace.FireTrace(component, name='int', separator='-')
    t.AddSeparator()
    help_screen = helptext.HelpText(component=component, trace=t, verbose=False)
    self.assertIn('int -', help_screen)
    self.assertNotIn('int - -', help_screen)

  def testHelpTextNameSectionCommandWithSeparatorVerbose(self):
    component = tc.WithDefaults().double
    t = trace.FireTrace(component, name='double', separator='-')
    t.AddSeparator()
    help_screen = helptext.HelpText(component=component, trace=t, verbose=True)
    self.assertIn('double -', help_screen)
    self.assertIn('double - -', help_screen)


class UsageTest(testutils.BaseTestCase):

  def testUsageOutput(self):
    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: NoDefaults <command>
      available commands:    double | triple

    For detailed information on this command, run:
      NoDefaults --help"""

    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputVerbose(self):
    component = tc.NoDefaults()
    t = trace.FireTrace(component, name='NoDefaults')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: NoDefaults <command>
      available commands:    double | triple

    For detailed information on this command, run:
      NoDefaults --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputMethod(self):
    component = tc.NoDefaults().double
    t = trace.FireTrace(component, name='NoDefaults')
    t.AddAccessedProperty(component, 'double', ['double'], None, None)
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: NoDefaults double COUNT

    For detailed information on this command, run:
      NoDefaults double --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithHelp(self):
    component = tc.function_with_help
    t = trace.FireTrace(component, name='function_with_help')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: function_with_help <flags>
      optional flags:        --help

    For detailed information on this command, run:
      function_with_help -- --help"""
    self.assertEqual(
        usage_output,
        textwrap.dedent(expected_output).lstrip('\n'))

  def testUsageOutputFunctionWithDocstring(self):
    component = tc.multiplier_with_docstring
    t = trace.FireTrace(component, name='multiplier_with_docstring')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: multiplier_with_docstring NUM <flags>
      optional flags:        --rate

    For detailed information on this command, run:
      multiplier_with_docstring --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputCallable(self):
    # This is both a group and a command.
    component = tc.CallableWithKeywordArgument()
    t = trace.FireTrace(component, name='CallableWithKeywordArgument',
                        separator='@')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: CallableWithKeywordArgument <command> | <flags>
      available commands:    print_msg
      flags are accepted

    For detailed information on this command, run:
      CallableWithKeywordArgument -- --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputConstructorWithParameter(self):
    component = tc.InstanceVars
    t = trace.FireTrace(component, name='InstanceVars')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = """
    Usage: InstanceVars --arg1=ARG1 --arg2=ARG2

    For detailed information on this command, run:
      InstanceVars --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputConstructorWithParameterVerbose(self):
    component = tc.InstanceVars
    t = trace.FireTrace(component, name='InstanceVars')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: InstanceVars <command> | --arg1=ARG1 --arg2=ARG2
      available commands:    run

    For detailed information on this command, run:
      InstanceVars --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputEmptyDict(self):
    component = {}
    t = trace.FireTrace(component, name='EmptyDict')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: EmptyDict

    For detailed information on this command, run:
      EmptyDict --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testUsageOutputNone(self):
    component = None
    t = trace.FireTrace(component, name='None')
    usage_output = helptext.UsageText(component, trace=t, verbose=True)
    expected_output = """
    Usage: None

    For detailed information on this command, run:
      None --help"""
    self.assertEqual(
        textwrap.dedent(expected_output).lstrip('\n'),
        usage_output)

  def testInitRequiresFlagSyntaxSubclassNamedTuple(self):
    component = tc.SubPoint
    t = trace.FireTrace(component, name='SubPoint')
    usage_output = helptext.UsageText(component, trace=t, verbose=False)
    expected_output = 'Usage: SubPoint --x=X --y=Y'
    self.assertIn(expected_output, usage_output)

if __name__ == '__main__':
  testutils.main()
