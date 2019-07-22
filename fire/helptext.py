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
from fire import decorators
from fire import formatting
from fire import inspectutils
from fire import value_types


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


def GetCurrentCommand(trace=None, include_separators=True):
  """Returns current command for the purpose of generating help text."""
  if trace:
    current_command = trace.GetCommand(include_separators=include_separators)
  else:
    current_command = ''
  return current_command


def HelpText(component, trace=None, verbose=False):
  info = inspectutils.Info(component)
  if inspect.isroutine(component) or inspect.isclass(component):
    return HelpTextForFunction(component, info, trace=trace, verbose=verbose)
  else:
    return HelpTextForObject(component, info, trace=trace, verbose=verbose)


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
  current_command_without_separator = GetCurrentCommand(
      trace, include_separators=False)
  summary, description = GetSummaryAndDescription(info['docstring_info'])

  args_with_no_defaults, args_with_defaults, flags = GetArgsAngFlags(component)
  del args_with_defaults

  # Name section
  name_section_template = '{current_command}{command_summary}'
  command_summary_str = ' - ' + summary if summary else ''
  name_section = name_section_template.format(
      current_command=current_command_without_separator,
      command_summary=command_summary_str)

  # Check if positional args are allowed. If not, require flag syntax for args.
  metadata = decorators.GetMetadata(component)
  accepts_positional_args = metadata.get(decorators.ACCEPTS_POSITIONAL_ARGS)

  arg_and_flag_strings = []
  if args_with_no_defaults:
    if accepts_positional_args:
      arg_strings = [formatting.Underline(arg.upper())
                     for arg in args_with_no_defaults]
    else:
      arg_strings = [
          '--{arg}={arg_upper}'.format(
              arg=arg, arg_upper=formatting.Underline(arg.upper()))
          for arg in args_with_no_defaults]
    arg_and_flag_strings.extend(arg_strings)

  flag_string_template = '[--{flag_name}={flag_name_upper}]'
  if flags:
    flag_strings = [
        flag_string_template.format(
            flag_name=formatting.Underline(flag), flag_name_upper=flag.upper())
        for flag in flags
    ]
    arg_and_flag_strings.extend(flag_strings)
  args_and_flags = ' '.join(arg_and_flag_strings)

  # Synopsis section
  synopsis_section_template = '{current_command} {args_and_flags}'
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

  arg_items = [
      _CreateArgItem(arg, docstring_info)
      for arg in args_with_no_defaults
  ]
  if arg_items:
    title = 'POSITIONAL ARGUMENTS' if accepts_positional_args else 'ARGUMENTS'
    arguments_section = (title, '\n'.join(arg_items).rstrip('\n'))
    args_and_flags_sections.append(arguments_section)
    if accepts_positional_args:
      notes_sections.append(
          ('NOTES', 'You can also use flags syntax for POSITIONAL ARGUMENTS')
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


def _CreateArgItem(arg, docstring_info):
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
    return _CreateItem(formatting.BoldUnderline(arg), description, indent=4)
  else:
    return formatting.BoldUnderline(arg)


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

  flag = '--{flag}'.format(flag=formatting.Underline(flag))
  if description:
    return _CreateItem(flag, description, indent=2)
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
  current_command_without_separator = GetCurrentCommand(
      trace, include_separators=False)
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
    possible_actions.append('GROUP')
    usage_details_section = GroupUsageDetailsSection(groups)
    usage_details_sections.append(usage_details_section)
  if commands:
    possible_actions.append('COMMAND')
    usage_details_section = CommandUsageDetailsSection(commands)
    usage_details_sections.append(usage_details_section)
  if values:
    possible_actions.append('VALUE')
    usage_details_section = ValuesUsageDetailsSection(component, values)
    usage_details_sections.append(usage_details_section)

  if isinstance(component, (list, tuple)) and component:
    possible_actions.append('INDEX')
    component_len = len(component)
    if component_len < 10:
      indexes_strings = [', '.join(str(x) for x in range(component_len))]
    else:
      indexes_strings = ['0..{max}'.format(max=component_len-1)]
    usage_details_sections.append(
        ('INDEXES', _NewChoicesSection('INDEX', indexes_strings)))

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
      current_command=current_command_without_separator,
      command_summary=command_summary)
  output_sections = [
      ('NAME', name_line),
      ('SYNOPSIS', synopsis_string),
  ] + description_sections + usage_details_sections

  return '\n\n'.join(
      _CreateOutputSection(name, content)
      for name, content in output_sections
  )


def GroupUsageDetailsSection(groups):
  """Creates a section tuple for the groups section of the usage details."""
  group_item_strings = []
  for group_name, group in groups:
    group_info = inspectutils.Info(group)
    group_item = group_name
    if 'docstring_info' in group_info:
      group_docstring_info = group_info['docstring_info']
      if group_docstring_info and group_docstring_info.summary:
        group_item = _CreateItem(group_name,
                                 group_docstring_info.summary)
    group_item_strings.append(group_item)
  return ('GROUPS', _NewChoicesSection('GROUP', group_item_strings))


def CommandUsageDetailsSection(commands):
  """Creates a section tuple for the commands section of the usage details."""
  command_item_strings = []
  for command_name, command in commands:
    command_info = inspectutils.Info(command)
    command_item = command_name
    if 'docstring_info' in command_info:
      command_docstring_info = command_info['docstring_info']
      if command_docstring_info and command_docstring_info.summary:
        command_item = _CreateItem(command_name,
                                   command_docstring_info.summary)
    command_item_strings.append(command_item)
  return ('COMMANDS', _NewChoicesSection('COMMAND', command_item_strings))


def ValuesUsageDetailsSection(component, values):
  """Creates a section tuple for the values section of the usage details."""
  value_item_strings = []
  for value_name, value in values:
    del value
    init_info = inspectutils.Info(component.__class__.__init__)
    value_item = None
    if 'docstring_info' in init_info:
      init_docstring_info = init_info['docstring_info']
      if init_docstring_info.args:
        for arg_info in init_docstring_info.args:
          if arg_info.name == value_name:
            value_item = _CreateItem(value_name, arg_info.description)
    if value_item is None:
      value_item = str(value_name)
    value_item_strings.append(value_item)
  return ('VALUES', _NewChoicesSection('VALUE', value_item_strings))


def _NewChoicesSection(name, choices):
  return _CreateItem(
      '{name} is one of the following:'.format(
          name=formatting.Bold(formatting.Underline(name))),
      '\n' + '\n\n'.join(choices),
      indent=1)


def UsageText(component, trace=None, verbose=False):
  if inspect.isroutine(component) or inspect.isclass(component):
    return UsageTextForFunction(component, trace, verbose)
  else:
    return UsageTextForObject(component, trace, verbose)


def UsageTextForFunction(component, trace=None, verbose=False):
  """Returns usage text for function objects.

  Args:
    component: The component to determine the usage text for.
    trace: The Fire trace object containing all metadata of current execution.
    verbose: Whether to display the usage text in verbose mode.

  Returns:
    String suitable for display in an error screen.
  """
  del verbose  # Unused.

  output_template = """Usage: {current_command} {args_and_flags}
{availability_lines}
For detailed information on this command, run:
  {current_command}{hyphen_hyphen} --help"""

  if trace:
    command = trace.GetCommand()
    needs_separating_hyphen_hyphen = trace.NeedsSeparatingHyphenHyphen()
  else:
    command = None
    needs_separating_hyphen_hyphen = False

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

  # Check if positional args are allowed. If not, show flag syntax for args.
  metadata = decorators.GetMetadata(component)
  accepts_positional_args = metadata.get(decorators.ACCEPTS_POSITIONAL_ARGS)
  if not accepts_positional_args:
    items = ['--{arg}={upper}'.format(arg=arg, upper=arg.upper())
             for arg in args_with_no_defaults]
  else:
    items = [arg.upper() for arg in args_with_no_defaults]

  if flags:
    items.append('<flags>')
    availability_lines = (
        '\nAvailable flags: '
        + ' | '.join('--' + flag for flag in flags) + '\n')
  else:
    availability_lines = ''
  args_and_flags = ' '.join(items)

  hyphen_hyphen = ' --' if needs_separating_hyphen_hyphen else ''

  return output_template.format(
      current_command=command,
      args_and_flags=args_and_flags,
      availability_lines=availability_lines,
      hyphen_hyphen=hyphen_hyphen)


def _CreateAvailabilityLine(header, items,
                            header_indent=2, items_indent=25, line_length=80):
  items_width = line_length - items_indent
  items_text = '\n'.join(formatting.WrappedJoin(items, width=items_width))
  indented_items_text = formatting.Indent(items_text, spaces=items_indent)
  indented_header = formatting.Indent(header, spaces=header_indent)
  return indented_header + indented_items_text[len(indented_header):] + '\n'


def UsageTextForObject(component, trace=None, verbose=False):
  """Returns the usage text for the error screen for an object.

  Constructs the usage text for the error screen to inform the user about how
  to use the current component.

  Args:
    component: The component to determine the usage text for.
    trace: The Fire trace object containing all metadata of current execution.
    verbose: Whether to include private members in the usage text.
  Returns:
    String suitable for display in error screen.
  """
  output_template = """Usage: {current_command}{possible_actions}
{availability_lines}
For detailed information on this command, run:
  {current_command} --help"""
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
    member_name = str(member_name)
    if value_types.IsGroup(member):
      groups.append(member_name)
    if value_types.IsCommand(member):
      commands.append(member_name)
    if value_types.IsValue(member):
      values.append(member_name)

  possible_actions = []
  availability_lines = []
  if groups:
    possible_actions.append('group')
    groups_text = _CreateAvailabilityLine(
        header='available groups:',
        items=groups)
    availability_lines.append(groups_text)
  if commands:
    possible_actions.append('command')
    commands_text = _CreateAvailabilityLine(
        header='available commands:',
        items=commands)
    availability_lines.append(commands_text)
  if values:
    possible_actions.append('value')
    values_text = _CreateAvailabilityLine(
        header='available values:',
        items=values)
    availability_lines.append(values_text)

  if isinstance(component, (list, tuple)) and component:
    possible_actions.append('index')
    component_len = len(component)
    if component_len < 10:
      indexes_strings = [str(x) for x in range(component_len)]
    else:
      indexes_strings = ['0..{max}'.format(max=component_len-1)]
    indexes_text = _CreateAvailabilityLine(
        header='available indexes:',
        items=indexes_strings)
    availability_lines.append(indexes_text)

  if possible_actions:
    possible_actions_string = ' <{actions}>'.format(
        actions='|'.join(possible_actions))
  else:
    possible_actions_string = ''

  availability_lines_string = ''.join(availability_lines)

  return output_template.format(
      current_command=command,
      possible_actions=possible_actions_string,
      availability_lines=availability_lines_string)
