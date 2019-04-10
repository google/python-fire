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

"""helptext is the new, work in progress, help text module for Fire.

This is a fork of, and is intended to replace, helputils.

Utility for producing help strings for use in Fire CLIs.

Can produce help strings suitable for display in Fire CLIs for any type of
Python object, module, class, or function.

There are two types of informative strings: Usage and Help screens.

Usage screens are shown when the user accesses a group or accesses a command
without calling it. A Usage screen shows information about how to use that group
or command. Usage screens are typically short and show the minimal information
necessary for the user to determine how to proceed.

Help screens are shown when the user requests help with the help flag (--help).
Help screens are shown in a less-style console view, and contain detailed help
information.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect

from fire import completion
from fire import docstrings
from fire import formatting
from fire import inspectutils
from fire import value_types


def HelpString(component, trace=None, verbose=False):
  """Returns the text to show for a supplied component.

  The component can be any Python class, object, function, module, etc.

  Args:
    component: The component to determine the help string for.
    trace: The Fire trace leading to this component.
    verbose: Whether to include private members in the help string.
  Returns:
    String suitable for display giving information about the component.
  """
  info = inspectutils.Info(component)
  info['docstring_info'] = docstrings.parse(info['docstring'])

  is_error_screen = False
  if trace:
    is_error_screen = trace.HasError()

  if is_error_screen:
    return UsageText(component, info, trace, verbose=verbose)
  else:
    return HelpText(component, info, trace, verbose=verbose)


def GetArgsAngFlags(component):
  """Returns all types of arguments and flags of a component."""
  spec = inspectutils.GetFullArgSpec(component)
  args = spec.args
  if spec.defaults is None:
    num_defaults = 0
  else:
    num_defaults = len(spec.defaults)
  args_with_no_defaults = args[:len(args) - num_defaults]
  args_with_defaults = args[len(args) - num_defaults:]
  flags = args_with_defaults + spec.kwonlyargs
  return args_with_no_defaults, args_with_defaults, flags


def GetSummaryAndDescription(docstring_info):
  """Retrieves summary and description for help text generation."""

  # To handle both empty string and None
  summary = docstring_info.summary if docstring_info.summary else None
  description = (
      docstring_info.description if docstring_info.description else None)
  return summary, description


def GetCurrentCommand(trace=None):
  """Returns current command for the purpose of generating help text."""
  if trace:
    current_command = trace.GetCommand()
  else:
    current_command = ''

  return current_command


def HelpText(component, info, trace=None, verbose=False):
  if inspect.isroutine(component) or inspect.isclass(component):
    return HelpTextForFunction(component, info, trace)
  else:
    return HelpTextForObject(component, info, trace, verbose)


def GetDescriptionSectionText(summary, description):
  """Returns description section text based on the input docstring info.

  Returns the string that should be used as description section based on the
  input. The logic is the following: If there's description available, use it.
  Otherwise, use summary if available. If neither description or summary is
  available, returns None.

  Args:
    summary: summary found in object summary
    description: description found in object docstring

  Returns:
    String for the description section in help screen.
  """
  if not (description or summary):
    return None

  if description:
    return description
  else:
    return summary


def HelpTextForFunction(component, info, trace=None, verbose=False):
  """Returns detail help text for a function component.

  Args:
    component: Current component to generate help text for.
    info: Info containing metadata of component.
    trace: FireTrace object that leads to current component.
    verbose: Whether to display help text in verbose mode.

  Returns:
    Formatted help text for display.
  """
  # TODO(joejoevictor): Implement verbose related output
  del verbose

  current_command = GetCurrentCommand(trace)
  summary, description = GetSummaryAndDescription(info['docstring_info'])
  spec = inspectutils.GetFullArgSpec(component)
  args = spec.args

  args_with_no_defaults, args_with_defaults, flags = GetArgsAngFlags(component)
  del args_with_defaults

  # Name section
  name_section_template = '{current_command}{command_summary}'
  command_summary_str = ' - ' + summary if summary else ''
  name_section = name_section_template.format(
      current_command=current_command, command_summary=command_summary_str)

  args_and_flags = ''
  if args_with_no_defaults:
    items = [arg.upper() for arg in args_with_no_defaults]
    args_and_flags = ' '.join(items)

  synopsis_flag_template = '[--{flag_name}={flag_name_upper}]'
  if flags:
    items = [
        synopsis_flag_template.format(
            flag_name=flag, flag_name_upper=flag.upper()) for flag in flags
    ]
    args_and_flags = args_and_flags + ' '.join(items)

  # Synopsis section
  synopsis_section_template = '{current_command} {args_and_flags}'
  positional_arguments = '|'.join(args)
  if positional_arguments:
    positional_arguments = ' ' + positional_arguments
  synopsis_section = synopsis_section_template.format(
      current_command=current_command, args_and_flags=args_and_flags)

  # Description section
  command_description = GetDescriptionSectionText(summary, description)
  description_sections = []
  if command_description:
    description_sections.append(('DESCRIPTION', command_description))

  # Positional arguments and flags section
  docstring_info = info['docstring_info']
  args_and_flags_sections = []
  notes_sections = []

  pos_arg_items = []
  pos_arg_items = [
      _CreatePositionalArgItem(arg, docstring_info)
      for arg in args_with_no_defaults
  ]
  if pos_arg_items:
    positional_arguments_section = ('POSITIONAL ARGUMENTS',
                                    '\n'.join(pos_arg_items).rstrip('\n'))
    args_and_flags_sections.append(positional_arguments_section)
    notes_sections.append(
        ('NOTES', 'You could also use flags syntax for POSITIONAL ARGUMENTS')
    )

  flag_items = [
      _CreateFlagItem(flag, docstring_info)
      for flag in flags
  ]

  if flag_items:
    flags_section = ('FLAGS', '\n'.join(flag_items))
    args_and_flags_sections.append(flags_section)

  output_sections = [
      ('NAME', name_section),
      ('SYNOPSIS', synopsis_section),
  ] + description_sections + args_and_flags_sections + notes_sections

  return '\n\n'.join(
      _CreateOutputSection(name, content)
      for name, content in output_sections
  )


def _CreateOutputSection(name, content):
  return """{name}
{content}""".format(name=formatting.Bold(name),
                    content=formatting.Indent(content, 4))


def _CreatePositionalArgItem(arg, docstring_info):
  """Returns a string describing a positional argument.

  Args:
    arg: The name of the positional argument.
    docstring_info: A docstrings.DocstringInfo namedtuple with information about
      the containing function's docstring.
  Returns:
    A string to be used in constructing the help screen for the function.
  """
  description = None
  if docstring_info.args:
    for arg_in_docstring in docstring_info.args:
      if arg_in_docstring.name == arg:
        description = arg_in_docstring.description

  arg = arg.upper()
  if description:
    return _CreateItem(arg, description, indent=4)
  else:
    return arg


def _CreateFlagItem(flag, docstring_info):
  """Returns a string describing a flag using information from the docstring.

  Args:
    flag: The name of the flag.
    docstring_info: A docstrings.DocstringInfo namedtuple with information about
      the containing function's docstring.
  Returns:
    A string to be used in constructing the help screen for the function.
  """
  description = None
  if docstring_info.args:
    for arg_in_docstring in docstring_info.args:
      if arg_in_docstring.name == flag:
        description = arg_in_docstring.description
        break

  flag = '--{flag}'.format(flag=flag)
  if description:
    return _CreateItem(flag, description, indent=2)
  else:
    return flag


def _CreateItem(name, description, indent=2):
  return """{name}
{description}""".format(name=name,
                        description=formatting.Indent(description, indent))


def HelpTextForObject(component, info, trace=None, verbose=False):
  """Generates help text for python objects.

  Args:
    component: Current component to generate help text for.
    info: Info containing metadata of component.
    trace: FireTrace object that leads to current component.
    verbose: Whether to display help text in verbose mode.

  Returns:
    Formatted help text for display.
  """
  current_command = GetCurrentCommand(trace)

  docstring_info = info['docstring_info']
  command_summary = docstring_info.summary if docstring_info.summary else ''
  command_description = GetDescriptionSectionText(docstring_info.summary,
                                                  docstring_info.description)
  groups = []
  commands = []
  values = []
  members = completion._Members(component, verbose)  # pylint: disable=protected-access
  for member_name, member in members:
    if value_types.IsGroup(member):
      groups.append((member_name, member))
    if value_types.IsCommand(member):
      commands.append((member_name, member))
    if value_types.IsValue(member):
      values.append((member_name, member))

  usage_details_sections = []
  possible_actions = []
  # TODO(joejoevictor): Add global flags to here. Also, if it's a callable,
  # there will be additional flags.
  possible_flags = ''

  if groups:
    # TODO(joejoevictor): Add missing GROUPS section handling
    possible_actions.append('GROUP')
  if commands:
    possible_actions.append('COMMAND')
    command_item_strings = []
    for command_name, command in commands:
      command_docstring_info = docstrings.parse(
          inspectutils.Info(command)['docstring'])
      command_item_strings.append(
          _CreateItem(command_name, command_docstring_info.summary))
    usage_details_sections.append(
        ('COMMANDS', _NewChoicesSection('COMMAND', command_item_strings)))

  if values:
    possible_actions.append('VALUE')
    value_item_strings = []
    for value_name, value in values:
      del value
      init_docstring_info = docstrings.parse(
          inspectutils.Info(component.__class__.__init__)['docstring'])
      for arg_info in init_docstring_info.args:
        if arg_info.name == value_name:
          value_item_strings.append(_CreateItem(value_name,
                                                arg_info.description))
    usage_details_sections.append(
        ('VALUES', _NewChoicesSection('VALUE', value_item_strings)))

  possible_actions_string = ' | '.join(
      formatting.Underline(action) for action in possible_actions)

  synopsis_template = '{current_command} {possible_actions}{possible_flags}'
  synopsis_string = synopsis_template.format(
      current_command=current_command,
      possible_actions=possible_actions_string,
      possible_flags=possible_flags)

  description_sections = []
  if command_description:
    description_sections.append(('DESCRIPTION', command_description))

  name_line = '{current_command} - {command_summary}'.format(
      current_command=current_command,
      command_summary=command_summary)
  output_sections = [
      ('NAME', name_line),
      ('SYNOPSIS', synopsis_string),
  ] + description_sections + usage_details_sections

  return '\n\n'.join(
      _CreateOutputSection(name, content)
      for name, content in output_sections
  )


def _NewChoicesSection(name, choices):
  return _CreateItem(
      '{name} is one of the followings:'.format(
          name=formatting.Bold(formatting.Underline(name))),
      '\n' + '\n\n'.join(choices),
      indent=1)


def UsageText(component, info, trace=None, verbose=False):
  del info  # Unused.
  if inspect.isroutine(component) or inspect.isclass(component):
    return UsageTextForFunction(component, trace)
  else:
    return UsageTextForObject(component, trace, verbose)


def UsageTextForFunction(component, trace=None):
  """Returns usage text for function objects.

  Args:
    component: The component to determine the usage text for.
    trace: The Fire trace object containing all metadata of current execution.

  Returns:
    String suitable for display in error screen.
  """

  output_template = """Usage: {current_command} {args_and_flags}
{availability_lines}
For detailed information on this command, run:
{current_command}{hyphen_hyphen} --help
"""

  if trace:
    command = trace.GetCommand()
    is_help_an_arg = trace.NeedsSeparatingHyphenHyphen()
  else:
    command = None
    is_help_an_arg = False

  if not command:
    command = ''

  spec = inspectutils.GetFullArgSpec(component)
  args = spec.args
  if spec.defaults is None:
    num_defaults = 0
  else:
    num_defaults = len(spec.defaults)
  args_with_no_defaults = args[:len(args) - num_defaults]
  args_with_defaults = args[len(args) - num_defaults:]
  flags = args_with_defaults + spec.kwonlyargs

  items = [arg.upper() for arg in args_with_no_defaults]
  if flags:
    items.append('<flags>')
    availability_lines = (
        '\nAvailable flags: '
        + ' | '.join('--' + flag for flag in flags) + '\n')
  else:
    availability_lines = ''
  args_and_flags = ' '.join(items)

  hyphen_hyphen = ' --' if is_help_an_arg else ''

  return output_template.format(
      current_command=command,
      args_and_flags=args_and_flags,
      availability_lines=availability_lines,
      hyphen_hyphen=hyphen_hyphen)


def UsageTextForObject(component, trace=None, verbose=False):
  """Returns help text for usage screen for objects.

  Construct help text for usage screen to inform the user about error occurred
  and correct syntax for invoking the object.

  Args:
    component: The component to determine the usage text for.
    trace: The Fire trace object containing all metadata of current execution.
    verbose: Whether to include private members in the usage text.
  Returns:
    String suitable for display in error screen.
  """
  output_template = """Usage: {current_command} <{possible_actions}>
{availability_lines}

For detailed information on this command and its flags, run:
{current_command} --help
"""
  if trace:
    command = trace.GetCommand()
  else:
    command = None

  if not command:
    command = ''

  groups = []
  commands = []
  values = []

  members = completion._Members(component, verbose)  # pylint: disable=protected-access
  for member_name, member in members:
    if value_types.IsGroup(member):
      groups.append(member_name)
    if value_types.IsCommand(member):
      commands.append(member_name)
    if value_types.IsValue(member):
      values.append(member_name)

  possible_actions = []
  availability_lines = []
  availability_lint_format = '{header:20s}{choices}'
  if groups:
    possible_actions.append('groups')
    groups_string = ' | '.join(groups)
    groups_text = availability_lint_format.format(
        header='available groups:',
        choices=groups_string)
    availability_lines.append(groups_text)
  if commands:
    possible_actions.append('commands')
    commands_string = ' | '.join(commands)
    commands_text = availability_lint_format.format(
        header='available commands:',
        choices=commands_string)
    availability_lines.append(commands_text)
  if values:
    possible_actions.append('values')
    values_string = ' | '.join(values)
    values_text = availability_lint_format.format(
        header='available values:',
        choices=values_string)
    availability_lines.append(values_text)
  possible_actions_string = '|'.join(possible_actions)
  availability_lines_string = '\n'.join(availability_lines)

  return output_template.format(
      current_command=command,
      possible_actions=possible_actions_string,
      availability_lines=availability_lines_string)
