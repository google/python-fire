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

"""Utilities for producing help strings for use in Fire CLIs.

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

from fire import completion
from fire import custom_descriptions
from fire import decorators
from fire import formatting
from fire import inspectutils
from fire import value_types

LINE_LENGTH = 80


def HelpText(component, trace=None, verbose=False):
  """Gets the help string for the current component, suitalbe for a help screen.

  Args:
    component: The component to construct the help string for.
    trace: The Fire trace of the command so far. The command executed so far
      can be extracted from this trace.
    verbose: Whether to include private members in the help screen.

  Returns:
    The full help screen as a string.
  """
  # Preprocessing needed to create the sections:
  info = inspectutils.Info(component)
  actions_grouped_by_kind = _GetActionsGroupedByKind(component, verbose=verbose)
  spec = inspectutils.GetFullArgSpec(component)
  metadata = decorators.GetMetadata(component)

  # Sections:
  name_section = _NameSection(component, info, trace=trace, verbose=verbose)
  synopsis_section = _SynopsisSection(
      component, actions_grouped_by_kind, spec, metadata, trace=trace)
  description_section = _DescriptionSection(component, info)
  # TODO(dbieber): Add returns and raises sections for functions.

  if callable(component):
    args_and_flags_sections, notes_sections = _ArgsAndFlagsSections(
        info, spec, metadata)
  else:
    args_and_flags_sections = []
    notes_sections = []
  usage_details_sections = _UsageDetailsSections(component,
                                                 actions_grouped_by_kind)

  sections = (
      [name_section, synopsis_section, description_section]
      + args_and_flags_sections
      + usage_details_sections
      + notes_sections
  )
  return '\n\n'.join(
      _CreateOutputSection(*section)
      for section in sections if section is not None
  )


def _NameSection(component, info, trace=None, verbose=False):
  """The "Name" section of the help string."""

  # Only include separators in the name in verbose mode.
  current_command = _GetCurrentCommand(trace, include_separators=verbose)
  summary = _GetSummary(info)

  # If the docstring is one of the messy builtin docstrings, don't show summary.
  # TODO(dbieber): In follow up commits we can add in replacement summaries.
  if custom_descriptions.NeedsCustomDescription(component):
    summary = None

  if summary:
    text = current_command + ' - ' + summary
  else:
    text = current_command
  return ('NAME', text)


def _SynopsisSection(component, actions_grouped_by_kind, spec, metadata,
                     trace=None):
  """The "Synopsis" section of the help string."""
  current_command = _GetCurrentCommand(trace=trace, include_separators=True)

  possible_actions = _GetPossibleActions(actions_grouped_by_kind)

  continuations = []
  if possible_actions:
    continuations.append(_GetPossibleActionsString(possible_actions))
  if callable(component):
    callable_continuation = _GetArgsAndFlagsString(spec, metadata)
    if callable_continuation:
      continuations.append(callable_continuation)
    elif trace:
      # This continuation might be blank if no args are needed.
      # In this case, show a separator.
      continuations.append(trace.separator)
  continuation = ' | '.join(continuations)

  synopsis_template = '{current_command} {continuation}'
  text = synopsis_template.format(
      current_command=current_command,
      continuation=continuation)

  return ('SYNOPSIS', text)


def _DescriptionSection(component, info):
  """The "Description" sections of the help string.

  Args:
    component: The component to produce the description section for.
    info: The info dict for the component of interest.

  Returns:
    Returns the description if available. If not, returns the summary.
    If neither are available, returns None.
  """
  # If the docstring is one of the messy builtin docstrings, set it to None.
  # TODO(dbieber): In follow up commits we can add in replacement docstrings.
  if custom_descriptions.NeedsCustomDescription(component):
    return None

  summary = _GetSummary(info)
  description = _GetDescription(info)
  text = description or summary or None

  if text:
    return ('DESCRIPTION', text)
  else:
    return None


def _ArgsAndFlagsSections(info, spec, metadata):
  """The "Args and Flags" sections of the help string."""
  args_with_no_defaults = spec.args[:len(spec.args) - len(spec.defaults)]
  args_with_defaults = spec.args[len(spec.args) - len(spec.defaults):]

  # Check if positional args are allowed. If not, require flag syntax for args.
  accepts_positional_args = metadata.get(decorators.ACCEPTS_POSITIONAL_ARGS)

  args_and_flags_sections = []
  notes_sections = []

  docstring_info = info['docstring_info']

  arg_items = [
      _CreateArgItem(arg, docstring_info)
      for arg in args_with_no_defaults
  ]

  if spec.varargs:
    arg_items.append(
        _CreateArgItem(spec.varargs, docstring_info)
    )

  if arg_items:
    title = 'POSITIONAL ARGUMENTS' if accepts_positional_args else 'ARGUMENTS'
    arguments_section = (title, '\n'.join(arg_items).rstrip('\n'))
    args_and_flags_sections.append(arguments_section)
    if args_with_no_defaults and accepts_positional_args:
      notes_sections.append(
          ('NOTES', 'You can also use flags syntax for POSITIONAL ARGUMENTS')
      )

  optional_flag_items = [
      _CreateFlagItem(flag, docstring_info, required=False)
      for flag in args_with_defaults
  ]
  required_flag_items = [
      _CreateFlagItem(flag, docstring_info, required=True)
      for flag in spec.kwonlyargs
  ]
  flag_items = optional_flag_items + required_flag_items

  if spec.varkw:
    description = _GetArgDescription(spec.varkw, docstring_info)
    message = ('Additional flags are accepted.'
               if flag_items else
               'Flags are accepted.')
    item = _CreateItem(message, description, indent=4)
    flag_items.append(item)

  if flag_items:
    flags_section = ('FLAGS', '\n'.join(flag_items))
    args_and_flags_sections.append(flags_section)

  return args_and_flags_sections, notes_sections


def _UsageDetailsSections(component, actions_grouped_by_kind):
  """The usage details sections of the help string."""
  groups, commands, values, indexes = actions_grouped_by_kind

  sections = []
  if groups.members:
    sections.append(_MakeUsageDetailsSection(groups))
  if commands.members:
    sections.append(_MakeUsageDetailsSection(commands))
  if values.members:
    sections.append(_ValuesUsageDetailsSection(component, values))
  if indexes.members:
    sections.append(('INDEXES', _NewChoicesSection('INDEX', indexes.names)))

  return sections


def _GetSummary(info):
  docstring_info = info['docstring_info']
  return docstring_info.summary if docstring_info.summary else None


def _GetDescription(info):
  docstring_info = info['docstring_info']
  return docstring_info.description if docstring_info.description else None


def _GetArgsAndFlagsString(spec, metadata):
  """The args and flags string for showing how to call a function.

  If positional arguments are accepted, the args will be shown as positional.
  E.g. "ARG1 ARG2 [--flag=FLAG]"

  If positional arguments are disallowed, the args will be shown with flags
  syntax.
  E.g. "--arg1=ARG1 [--flag=FLAG]"

  Args:
    spec: The full arg spec for the component to construct the args and flags
      string for.
    metadata: Metadata for the component, including whether it accepts
      positional arguments.

  Returns:
    The constructed args and flags string.
  """
  args_with_no_defaults = spec.args[:len(spec.args) - len(spec.defaults)]
  args_with_defaults = spec.args[len(spec.args) - len(spec.defaults):]

  # Check if positional args are allowed. If not, require flag syntax for args.
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

  # If there are any arguments that are treated as flags:
  if args_with_defaults or spec.kwonlyargs or spec.varkw:
    arg_and_flag_strings.append('<flags>')

  if spec.varargs:
    varargs_string = '[{varargs}]...'.format(
        varargs=formatting.Underline(spec.varargs.upper()))
    arg_and_flag_strings.append(varargs_string)

  return ' '.join(arg_and_flag_strings)


def _GetPossibleActions(actions_grouped_by_kind):
  """The list of possible action kinds."""
  possible_actions = []
  for action_group in actions_grouped_by_kind:
    if action_group.members:
      possible_actions.append(action_group.name)
  return possible_actions


def _GetPossibleActionsString(possible_actions):
  """A help screen string listing the possible action kinds available."""
  return ' | '.join(formatting.Underline(action.upper())
                    for action in possible_actions)


def _GetActionsGroupedByKind(component, verbose=False):
  """Gets lists of available actions, grouped by action kind."""
  groups = ActionGroup(name='group', plural='groups')
  commands = ActionGroup(name='command', plural='commands')
  values = ActionGroup(name='value', plural='values')
  indexes = ActionGroup(name='index', plural='indexes')

  members = completion.VisibleMembers(component, verbose=verbose)
  for member_name, member in members:
    member_name = str(member_name)
    if value_types.IsGroup(member):
      groups.Add(name=member_name, member=member)
    if value_types.IsCommand(member):
      commands.Add(name=member_name, member=member)
    if value_types.IsValue(member):
      values.Add(name=member_name, member=member)

  if isinstance(component, (list, tuple)) and component:
    component_len = len(component)
    if component_len < 10:
      indexes.Add(name=', '.join(str(x) for x in range(component_len)))
    else:
      indexes.Add(name='0..{max}'.format(max=component_len-1))

  return [groups, commands, values, indexes]


def _GetCurrentCommand(trace=None, include_separators=True):
  """Returns current command for the purpose of generating help text."""
  if trace:
    current_command = trace.GetCommand(include_separators=include_separators)
  else:
    current_command = ''
  return current_command


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
  description = _GetArgDescription(arg, docstring_info)

  arg = arg.upper()
  return _CreateItem(formatting.BoldUnderline(arg), description, indent=4)


def _CreateFlagItem(flag, docstring_info, required=False):
  """Returns a string describing a flag using information from the docstring.

  Args:
    flag: The name of the flag.
    docstring_info: A docstrings.DocstringInfo namedtuple with information about
      the containing function's docstring.
    required: Whether the flag is required. Keyword-only arguments (only in
      Python 3) become required flags, whereas normal keyword arguments become
      optional flags.
  Returns:
    A string to be used in constructing the help screen for the function.
  """
  description = _GetArgDescription(flag, docstring_info)

  flag_string_template = '--{flag_name}={flag_name_upper}'
  flag = flag_string_template.format(
      flag_name=flag,
      flag_name_upper=formatting.Underline(flag.upper()))
  if required:
    flag += ' (required)'
  return _CreateItem(flag, description, indent=4)


def _CreateItem(name, description, indent=2):
  if not description:
    return name
  return """{name}
{description}""".format(name=name,
                        description=formatting.Indent(description, indent))


def _GetArgDescription(name, docstring_info):
  if docstring_info.args:
    for arg_in_docstring in docstring_info.args:
      if arg_in_docstring.name in (name, '*' + name, '**' + name):
        return arg_in_docstring.description
  return None


def _MakeUsageDetailsSection(action_group):
  """Creates a usage details section for the provided action group."""
  item_strings = []
  for name, member in action_group.GetItems():
    info = inspectutils.Info(member)
    item = name
    docstring_info = info.get('docstring_info')
    if (docstring_info
        and not custom_descriptions.NeedsCustomDescription(member)):
      summary = docstring_info.summary
    else:
      summary = None
    item = _CreateItem(name, summary)
    item_strings.append(item)
  return (action_group.plural.upper(),
          _NewChoicesSection(action_group.name.upper(), item_strings))


def _ValuesUsageDetailsSection(component, values):
  """Creates a section tuple for the values section of the usage details."""
  value_item_strings = []
  for value_name, value in values.GetItems():
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
  """Returns usage text for the given component.

  Args:
    component: The component to determine the usage text for.
    trace: The Fire trace object containing all metadata of current execution.
    verbose: Whether to display the usage text in verbose mode.

  Returns:
    String suitable for display in an error screen.
  """
  output_template = """Usage: {continued_command}
{availability_lines}
For detailed information on this command, run:
  {help_command}"""

  # Get the command so far:
  if trace:
    command = trace.GetCommand()
    needs_separating_hyphen_hyphen = trace.NeedsSeparatingHyphenHyphen()
  else:
    command = None
    needs_separating_hyphen_hyphen = False

  if not command:
    command = ''

  # Build the continuations for the command:
  continued_command = command

  spec = inspectutils.GetFullArgSpec(component)
  metadata = decorators.GetMetadata(component)

  # Usage for objects.
  actions_grouped_by_kind = _GetActionsGroupedByKind(component, verbose=verbose)
  possible_actions = _GetPossibleActions(actions_grouped_by_kind)

  continuations = []
  if possible_actions:
    continuations.append(_GetPossibleActionsUsageString(possible_actions))

  availability_lines = _UsageAvailabilityLines(actions_grouped_by_kind)

  if callable(component):
    callable_items = _GetCallableUsageItems(spec, metadata)
    if callable_items:
      continuations.append(' '.join(callable_items))
    elif trace:
      continuations.append(trace.separator)
    availability_lines.extend(_GetCallableAvailabilityLines(spec))

  if continuations:
    continued_command += ' ' + ' | '.join(continuations)
  help_command = (
      command
      + (' -- ' if needs_separating_hyphen_hyphen else ' ')
      + '--help'
  )

  return output_template.format(
      continued_command=continued_command,
      availability_lines=''.join(availability_lines),
      help_command=help_command)


def _GetPossibleActionsUsageString(possible_actions):
  if possible_actions:
    return '<{actions}>'.format(actions='|'.join(possible_actions))
  return None


def _UsageAvailabilityLines(actions_grouped_by_kind):
  availability_lines = []
  for action_group in actions_grouped_by_kind:
    if action_group.members:
      availability_line = _CreateAvailabilityLine(
          header='available {plural}:'.format(plural=action_group.plural),
          items=action_group.names
      )
      availability_lines.append(availability_line)
  return availability_lines


def _GetCallableUsageItems(spec, metadata):
  """A list of elements that comprise the usage summary for a callable."""
  args_with_no_defaults = spec.args[:len(spec.args) - len(spec.defaults)]
  args_with_defaults = spec.args[len(spec.args) - len(spec.defaults):]

  # Check if positional args are allowed. If not, show flag syntax for args.
  accepts_positional_args = metadata.get(decorators.ACCEPTS_POSITIONAL_ARGS)

  if not accepts_positional_args:
    items = ['--{arg}={upper}'.format(arg=arg, upper=arg.upper())
             for arg in args_with_no_defaults]
  else:
    items = [arg.upper() for arg in args_with_no_defaults]

  # If there are any arguments that are treated as flags:
  if args_with_defaults or spec.kwonlyargs or spec.varkw:
    items.append('<flags>')

  if spec.varargs:
    items.append('[{varargs}]...'.format(varargs=spec.varargs.upper()))

  return items


def _GetCallableAvailabilityLines(spec):
  """The list of availability lines for a callable for use in a usage string."""
  args_with_defaults = spec.args[len(spec.args) - len(spec.defaults):]

  # TODO(dbieber): Handle args_with_no_defaults if not accepts_positional_args.
  optional_flags = [('--' + flag) for flag in args_with_defaults]
  required_flags = [('--' + flag) for flag in spec.kwonlyargs]

  # Flags section:
  availability_lines = []
  if optional_flags:
    availability_lines.append(
        _CreateAvailabilityLine(header='optional flags:', items=optional_flags,
                                header_indent=2))
  if required_flags:
    availability_lines.append(
        _CreateAvailabilityLine(header='required flags:', items=required_flags,
                                header_indent=2))
  if spec.varkw:
    additional_flags = ('additional flags are accepted'
                        if optional_flags or required_flags else
                        'flags are accepted')
    availability_lines.append(
        _CreateAvailabilityLine(header=additional_flags, items=[],
                                header_indent=2))
  return availability_lines


def _CreateAvailabilityLine(header, items,
                            header_indent=2, items_indent=25,
                            line_length=LINE_LENGTH):
  items_width = line_length - items_indent
  items_text = '\n'.join(formatting.WrappedJoin(items, width=items_width))
  indented_items_text = formatting.Indent(items_text, spaces=items_indent)
  indented_header = formatting.Indent(header, spaces=header_indent)
  return indented_header + indented_items_text[len(indented_header):] + '\n'


class ActionGroup(object):
  """A group of actions of the same kind."""

  def __init__(self, name, plural):
    self.name = name
    self.plural = plural
    self.names = []
    self.members = []

  def Add(self, name, member=None):
    self.names.append(name)
    self.members.append(member)

  def GetItems(self):
    return zip(self.names, self.members)
