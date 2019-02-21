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

"""Utility for producing help strings for use in Fire CLIs.

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
from fire import inspectutils
from fire import value_types


def _NormalizeField(field):
  """Takes a field name and turns it into a human readable name for display.

  Args:
    field: The field name, used to index into the inspection dict.
  Returns:
    The human readable name, suitable for display in a help string.
  """
  if field == 'type_name':
    field = 'type'
  return (field[0].upper() + field[1:]).replace('_', ' ')


def _DisplayValue(info, field, padding):
  """Gets the value of field from the dict info for display.

  Args:
    info: The dict with information about the component.
    field: The field to access for display.
    padding: Number of spaces to indent text to line up with first-line text.
  Returns:
    The value of the field for display, or None if no value should be displayed.
  """
  value = info.get(field)

  if value is None:
    return None

  skip_doc_types = ('dict', 'list', 'unicode', 'int', 'float', 'bool')

  if field == 'docstring':
    if info.get('type_name') in skip_doc_types:
      # Don't show the boring default docstrings for these types.
      return None
    elif value == '<no docstring>':
      return None

  elif field == 'usage':
    lines = []
    for index, line in enumerate(value.split('\n')):
      if index > 0:
        line = ' ' * padding + line
      lines.append(line)
    return '\n'.join(lines)

  return value


def _GetFields(trace=None):
  """Returns the field names to include in the help text for a component."""
  del trace  # Unused.
  return [
      'type_name',
      'string_form',
      'file',
      'line',
      'docstring',
      'init_docstring',
      'class_docstring',
      'call_docstring',
      'length',
      'usage',
  ]


def HelpString(component, trace=None, verbose=False):
  """Returns a help string for a supplied component.

  The component can be any Python class, object, function, module, etc.

  Args:
    component: The component to determine the help string for.
    trace: The Fire trace leading to this component.
    verbose: Whether to include private members in the help string.
  Returns:
    String suitable for display giving information about the component.
  """
  info = inspectutils.Info(component)
  # TODO(dbieber): Stop using UsageString in favor of UsageText.
  info['usage'] = UsageString(component, trace, verbose)
  info['docstring_info'] = docstrings.parse(info['docstring'])

  is_error_screen = False
  if trace:
    is_error_screen = trace.HasError()

  if is_error_screen:
    # TODO(dbieber): Call UsageText instead of CommonHelpText once ready.
    return _CommonHelpText(info, trace)
  else:
    return _HelpText(info, trace)


def _CommonHelpText(info, trace=None):
  """Returns help text.

  This was a copy of previous HelpString function and will be removed once the
  correct text formatters are implemented.

  Args:
    info: The IR object containing metadata of an object.
    trace: The Fire trace object containing all metadata of current execution.
  Returns:
    String suitable for display giving information about the component.
  """
  # TODO(joejoevictor): Currently this is just a copy of existing
  # HelpString method. We will reimplement this further in later CLs.
  fields = _GetFields(trace)

  try:
    max_size = max(
        len(_NormalizeField(field)) + 1
        for field in fields
        if field in info and info[field])
    format_string = '{{field:{max_size}s}} {{value}}'.format(max_size=max_size)
  except ValueError:
    return ''

  lines = []
  for field in fields:
    value = _DisplayValue(info, field, padding=max_size + 1)
    if value:
      if lines and field == 'usage':
        lines.append('')  # Ensure a blank line before usage.

      lines.append(format_string.format(
          field=_NormalizeField(field) + ':',
          value=value,
      ))
  return '\n'.join(lines)


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

  if spec.defaults is None:
    num_defaults = 0
  else:
    num_defaults = len(spec.defaults)
  args_with_no_defaults = args[:len(args) - num_defaults]

  # TODO(joejoevictor): Generate flag section using these
  # args_with_defaults = args[len(args) - num_defaults:]
  # flags = args_with_defaults + spec.kwonlyargs

  output_template = """NAME
    {name_section}

SYNOPSIS
    {synopsis_section}

DESCRIPTION
    {description_section}
{args_and_flags_section}
NOTES
    You could also use flags syntax for POSITIONAL ARGUMENTS
"""

  # Name section
  name_section_template = '{current_command}{command_summary}'
  command_summary_str = ' - ' + summary if summary else ''
  name_section = name_section_template.format(
      current_command=current_command, command_summary=command_summary_str)

  items = [arg.upper() for arg in args_with_no_defaults]
  args_and_flags = ' '.join(items)

  # Synopsis section
  synopsis_section_template = '{current_command} {args_and_flags}'
  positional_arguments = '|'.join(args)
  if positional_arguments:
    positional_arguments = ' ' + positional_arguments
  synopsis_section = synopsis_section_template.format(
      current_command=current_command, args_and_flags=args_and_flags)

  # Description section
  description_section = description if description else summary

  args_and_flags_section = ''

  # Positional arguments and flags section

  pos_arg_template = """
POSITIONAL ARGUMENTS
{items}
"""
  pos_arg_items = []
  for arg in args_with_no_defaults:
    item_template = '    {arg_name}\n        {arg_description}\n'
    arg_description = None
    for arg_in_docstring in info['docstring_info'].args:
      if arg_in_docstring.name == arg:
        arg_description = arg_in_docstring.description

    item = item_template.format(
        arg_name=arg.upper(), arg_description=arg_description)
    pos_arg_items.append(item)
  if pos_arg_items:
    args_and_flags_section += pos_arg_template.format(
        items='\n'.join(pos_arg_items).rstrip('\n'))

  return output_template.format(
      name_section=name_section,
      synopsis_section=synopsis_section,
      description_section=description_section,
      args_and_flags_section=args_and_flags_section)


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

  output_template = """NAME
    {current_command} - {command_summary}

SYNOPSIS
    {synopsis}

DESCRIPTION
    {command_description}
{detail_section}
"""

  current_command = GetCurrentCommand(trace)

  docstring_info = info['docstring_info']
  command_summary = docstring_info.summary if docstring_info.summary else ''
  if docstring_info.description:
    command_description = docstring_info.description
  else:
    command_description = ''

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

  possible_actions = []
  # TODO(joejoevictor): Add global flags to here. Also, if it's a callable,
  # there will be additional flags.
  possible_flags = ''
  detail_section_string = ''
  item_template = """
        {name}
            {command_summary}
"""

  if groups:
    # TODO(joejoevictor): Add missing GROUPS section handling
    possible_actions.append('GROUP')
  if commands:
    possible_actions.append('COMMAND')
    commands_str_template = """
COMMANDS
    COMMAND is one of the followings:
{items}
"""
    command_item_strings = []
    for command_name, command in commands:
      command_docstring_info = docstrings.parse(
          inspectutils.Info(command)['docstring'])
      command_item_strings.append(
          item_template.format(
              name=command_name,
              command_summary=command_docstring_info.summary))
    detail_section_string += commands_str_template.format(
        items=('\n'.join(command_item_strings)).rstrip('\n'))

  if values:
    possible_actions.append('VALUES')
    values_str_template = """
VALUES
    VALUE is one of the followings:
{items}
"""
    value_item_strings = []
    for value_name, value in values:
      del value
      init_docstring_info = docstrings.parse(
          inspectutils.Info(component.__class__.__init__)['docstring'])
      for arg_info in init_docstring_info.args:
        if arg_info.name == value_name:
          value_item_strings.append(
              item_template.format(
                  name=value_name, command_summary=arg_info.description))
    detail_section_string += values_str_template.format(
        items=('\n'.join(value_item_strings)).rstrip('\n'))

  possible_actions_string = ' ' + (' | '.join(possible_actions))

  synopsis_template = '{current_command}{possible_actions}{possible_flags}'
  synopsis_string = synopsis_template.format(
      current_command=current_command,
      possible_actions=possible_actions_string,
      possible_flags=possible_flags)

  return output_template.format(
      current_command=current_command,
      command_summary=command_summary,
      synopsis=synopsis_string,
      command_description=command_description,
      detail_section=detail_section_string)


def UsageText(component, trace=None, verbose=False):
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

For detailed information on this command, run:
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


def _HelpText(info, trace=None):
  """Returns help text for extensive help screen.

  Construct help text for help screen when user explicitly requesting help by
  having -h, --help in the command sequence.

  Args:
    info: The IR object containing metadata of an object.
    trace: The Fire trace object containing all metadata of current execution.
  Returns:
    String suitable for display in extensive help screen.
  """

  # TODO(joejoevictor): Implement real help text construction.
  return _CommonHelpText(info, trace)


def _UsageStringFromFullArgSpec(command, spec):
  """Get a usage string from the FullArgSpec for the given command.

  The strings look like:
  command --arg ARG [--opt OPT] [VAR ...] [--KWARGS ...]

  Args:
    command: The command leading up to the function.
    spec: a FullArgSpec object describing the function.
  Returns:
    The usage string for the function.
  """
  num_required_args = len(spec.args) - len(spec.defaults)

  help_flags = []
  help_positional = []
  for index, arg in enumerate(spec.args):
    flag = arg.replace('_', '-')
    if index < num_required_args:
      help_flags.append('--{flag} {value}'.format(flag=flag, value=arg.upper()))
      help_positional.append('{value}'.format(value=arg.upper()))
    else:
      help_flags.append('[--{flag} {value}]'.format(
          flag=flag, value=arg.upper()))
      help_positional.append('[{value}]'.format(value=arg.upper()))

  if spec.varargs:
    help_flags.append('[{var} ...]'.format(var=spec.varargs.upper()))
    help_positional.append('[{var} ...]'.format(var=spec.varargs.upper()))

  for arg in spec.kwonlyargs:
    if arg in spec.kwonlydefaults:
      arg_str = '[--{flag} {value}]'.format(flag=arg, value=arg.upper())
    else:
      arg_str = '--{flag} {value}'.format(flag=arg, value=arg.upper())
    help_flags.append(arg_str)
    help_positional.append(arg_str)

  if spec.varkw:
    help_flags.append('[--{kwarg} ...]'.format(kwarg=spec.varkw.upper()))
    help_positional.append('[--{kwarg} ...]'.format(kwarg=spec.varkw.upper()))

  commands_flags = command + ' '.join(help_flags)
  commands_positional = command + ' '.join(help_positional)
  commands = [commands_positional]

  if commands_flags != commands_positional:
    commands.append(commands_flags)

  return '\n'.join(commands)


def UsageString(component, trace=None, verbose=False):
  """Returns a string showing how to use the component as a Fire command."""
  if trace:
    command = trace.GetCommand()
  else:
    command = None

  if command:
    command += ' '
  else:
    command = ''

  if inspect.isroutine(component) or inspect.isclass(component):
    spec = inspectutils.GetFullArgSpec(component)
    return _UsageStringFromFullArgSpec(command, spec)

  if isinstance(component, (list, tuple)):
    length = len(component)
    if length == 0:
      return command
    if length == 1:
      return command + '[0]'
    return command + '[0..{cap}]'.format(cap=length - 1)

  completions = completion.Completions(component, verbose)
  if command:
    completions = [''] + completions
  return '\n'.join(command + end for end in completions)
