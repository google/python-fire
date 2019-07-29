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

"""Docstring parsing module for Python Fire.

The following features of docstrings are not supported.
TODO(dbieber): Support these features.
- numpy docstrings may begin with the function signature.
- whitespace may be important for proper structuring of a docstring
- I've seen `argname` (with single backticks) as a style of documenting
  arguments. The `argname` appears on one line, and the description on the next.
- .. Sphinx directives such as .. note:: are not understood.
- After a section ends, future contents may be included in the section. E.g.
  :returns: This is what is returned.
  Example: An example goes here.
- @param is sometimes used.  E.g.
  @param argname (type) Description
  @return (type) Description
- The true signature of a function is not used by the docstring parser. It could
  be useful for determining whether something is a section header or an argument
  for example.
- This example confuses types as part of the docstrings.
  Parameters
  argname : argtype
  Arg description
- If there's no blank line after the summary, the description will be slurped
  up into the summary.
- "Examples" should be its own section type. aka "Usage".
- "Notes" should be a section type.
- Some people put parenthesis around their types in RST format, e.g.
  :param (type) paramname:
- :rtype: directive (return type)
- Also ":rtype str" with no closing ":" has come up.
- Return types are not supported.
- "# Returns" as a section title style
- ":raises ExceptionType: Description" ignores the ExceptionType currently.
- "Defaults to X" occurs sometimes.
- "True | False" indicates bool type.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import collections
import re
import textwrap

import enum


class DocstringInfo(
    collections.namedtuple(
        'DocstringInfo',
        ('summary', 'description', 'args', 'returns', 'yields', 'raises'))):
  pass
DocstringInfo.__new__.__defaults__ = (None,) * len(DocstringInfo._fields)


class ArgInfo(
    collections.namedtuple(
        'ArgInfo',
        ('name', 'type', 'description'))):
  pass
ArgInfo.__new__.__defaults__ = (None,) * len(ArgInfo._fields)


class Namespace(dict):
  """A dict with attribute (dot-notation) access enabled."""

  def __getattr__(self, key):
    if key not in self:
      self[key] = Namespace()
    return self[key]

  def __setattr__(self, key, value):
    self[key] = value

  def __delattr__(self, key):
    if key in self:
      del self[key]


class Sections(enum.Enum):
  ARGS = 0
  RETURNS = 1
  YIELDS = 2
  RAISES = 3
  TYPE = 4


class Formats(enum.Enum):
  GOOGLE = 0
  NUMPY = 1
  RST = 2


SECTION_TITLES = {
    Sections.ARGS: ('argument', 'arg', 'parameter', 'param'),
    Sections.RETURNS: ('return',),
    Sections.YIELDS: ('yield',),
    Sections.RAISES: ('raise', 'except', 'exception', 'throw', 'error', 'warn'),
    Sections.TYPE: ('type',),  # rst-only
}


def parse(docstring):
  """Returns DocstringInfo about the given docstring.

  This parser aims to parse Google, numpy, and rst formatted docstrings. These
  are the three most common docstring styles at the time of this writing.

  This parser aims to be permissive, working even when the docstring deviates
  from the strict recommendations of these styles.

  This parser does not aim to fully extract all structured information from a
  docstring, since there are simply too many ways to structure information in a
  docstring. Sometimes content will remain as unstructured text and simply gets
  included in the description.

  The Google docstring style guide is available at:
  https://github.com/google/styleguide/blob/gh-pages/pyguide.md

  The numpy docstring style guide is available at:
  https://numpydoc.readthedocs.io/en/latest/format.html

  Information about the rST docstring format is available at:
  https://www.python.org/dev/peps/pep-0287/
  The full set of directives such as param and type for rST docstrings are at:
  http://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html

  Note: This function does not claim to handle all docstrings well. A list of
  limitations is available at the top of the file. It does aim to run without
  crashing in O(n) time on all strings on length n. If you find a string that
  causes this to crash or run unacceptably slowly, please consider submitting
  a pull request.

  Args:
    docstring: The docstring to parse.
  Returns:
    A DocstringInfo containing information about the docstring.
  """
  if docstring is None:
    return DocstringInfo()

  lines = docstring.strip().split('\n')
  lines_len = len(lines)
  state = Namespace()  # TODO(dbieber): Switch to an explicit class.

  # Variables in state include:
  state.section.title = None
  state.section.indentation = None
  state.section.line1_indentation = None
  state.section.format = None
  state.summary.permitted = True
  state.summary.lines = []
  state.description.lines = []
  state.args = []
  state.current_arg = None
  state.returns.lines = []
  state.yields.lines = []
  state.raises.lines = []

  for index, line in enumerate(lines):
    has_next = index + 1 < lines_len
    next_line = lines[index + 1] if has_next else None
    line_info = _create_line_info(line, next_line)
    _consume_line(line_info, state)

  summary = ' '.join(state.summary.lines) if state.summary.lines else None
  state.description.lines = _strip_blank_lines(state.description.lines)
  description = textwrap.dedent('\n'.join(state.description.lines))
  if not description:
    description = None
  returns = _join_lines(state.returns.lines)
  yields = _join_lines(state.yields.lines)
  raises = _join_lines(state.raises.lines)

  args = [ArgInfo(
      name=arg.name, type=_cast_to_known_type(_join_lines(arg.type.lines)),
      description=_join_lines(arg.description.lines)) for arg in state.args]

  return DocstringInfo(
      summary=summary,
      description=description,
      args=args or None,
      returns=returns,
      raises=raises,
      yields=yields,
  )


def _strip_blank_lines(lines):
  """Removes lines containing only blank characters before and after the text.

  Args:
    lines: A list of lines.
  Returns:
    A list of lines without trailing or leading blank lines.
  """
  # Find the first non-blank line.
  start = 0
  while lines and _is_blank(lines[start]):
    start += 1

  lines = lines[start:]

  # Remove trailing blank lines.
  while lines and _is_blank(lines[-1]):
    lines.pop()

  return lines


def _is_blank(line):
  return not line or line.isspace()


def _join_lines(lines):
  """Joins lines with the appropriate connective whitespace.

  This puts a single space between consecutive lines, unless there's a blank
  line, in which case a full blank line is included.

  Args:
    lines: A list of lines to join.
  Returns:
    A string, the lines joined together.
  """
  # TODO(dbieber): Add parameters for variations in whitespace handling.
  if not lines:
    return None

  started = False
  group_texts = []  # Full text of each section.
  group_lines = []  # Lines within the current section.
  for line in lines:
    stripped_line = line.strip()
    if stripped_line:
      started = True
      group_lines.append(stripped_line)
    else:
      if started:
        group_text = ' '.join(group_lines)
        group_texts.append(group_text)
        group_lines = []

  if group_lines:  # Process the final group.
    group_text = ' '.join(group_lines)
    group_texts.append(group_text)

  return '\n\n'.join(group_texts)


def _get_or_create_arg_by_name(state, name):
  """Gets or creates a new Arg.

  These Arg objects (Namespaces) are turned into the ArgInfo namedtuples
  returned by parse. Each Arg object is used to collect the name, type, and
  description of a single argument to the docstring's function.

  Args:
    state: The state of the parser.
    name: The name of the arg to create.
  Returns:
    The new Arg.
  """
  for arg in state.args:
    if arg.name == name:
      return arg
  arg = Namespace()  # TODO(dbieber): Switch to an explicit class.
  arg.name = name
  arg.type.lines = []
  arg.description.lines = []
  state.args.append(arg)
  return arg


def _is_arg_name(name):
  """Returns whether name is a valid arg name.

  This is used to prevent multiple words (plaintext) from being misinterpreted
  as an argument name. So if ":" appears in the middle of a line in a docstring,
  we don't accidentally interpret the first half of that line as a single arg
  name.

  Args:
    name: The name of the potential arg.
  Returns:
    True if name looks like an arg name, False otherwise.
  """
  name = name.strip()
  return (name
          and ' ' not in name
          and ':' not in name)


def _as_arg_name_and_type(text):
  """Returns text as a name and type, if text looks like an arg name and type.

  Example:
    _as_arg_name_and_type("foo (int)") == "foo", "int"

  Args:
    text: The text, which may or may not be an arg name and type.
  Returns:
    The arg name and type, if text looks like an arg name and type.
    None otherwise.
  """
  tokens = text.split()
  if len(tokens) < 2:
    return None
  if _is_arg_name(tokens[0]):
    type_token = ' '.join(tokens[1:])
    type_token = type_token.lstrip('{([').rstrip('])}')
    return tokens[0], type_token
  else:
    return None


def _as_arg_names(names_str):
  """Converts names_str to a list of arg names.

  Example:
    _as_arg_names("a, b, c") == ["a", "b", "c"]

  Args:
    names_str: A string with multiple space or comma separated arg names.
  Returns:
    A list of arg names, or None if names_str doesn't look like a list of arg
    names.
  """
  names = re.split(',| ', names_str)
  names = [name.strip() for name in names if name.strip()]
  for name in names:
    if not _is_arg_name(name):
      return None
  if not names:
    return None
  return names


def _cast_to_known_type(name):
  """Canonicalizes a string representing a type if possible.

  # TODO(dbieber): Support additional canonicalization, such as string/str, and
  # boolean/bool.

  Example:
    _cast_to_known_type("str.") == "str"

  Args:
    name: A string representing a type, or None.
  Returns:
    A canonicalized version of the type string.
  """
  if name is None:
    return None
  return name.rstrip('.')


def _consume_google_args_line(line_info, state):
  """Consume a single line from a Google args section."""
  split_line = line_info.remaining.split(':', 1)
  if len(split_line) > 1:
    first, second = split_line  # first is either the "arg" or "arg (type)"
    if _is_arg_name(first.strip()):
      arg = _get_or_create_arg_by_name(state, first.strip())
      arg.description.lines.append(second.strip())
      state.current_arg = arg
    else:
      arg_name_and_type = _as_arg_name_and_type(first)
      if arg_name_and_type:
        arg_name, type_str = arg_name_and_type
        arg = _get_or_create_arg_by_name(state, arg_name)
        arg.type.lines.append(type_str)
        arg.description.lines.append(second.strip())
      else:
        if state.current_arg:
          state.current_arg.description.lines.append(split_line[0])
  else:
    if state.current_arg:
      state.current_arg.description.lines.append(split_line[0])


def _consume_line(line_info, state):
  """Consumes one line of text, updating the state accordingly.

  When _consume_line is called, part of the line may already have been processed
  for header information.

  Args:
    line_info: Information about the current and next line of the docstring.
    state: The state of the docstring parser.
  """
  _update_section_state(line_info, state)

  if state.section.title is None:
    if state.summary.permitted:
      if line_info.remaining:
        state.summary.lines.append(line_info.remaining)
      elif state.summary.lines:
        state.summary.permitted = False
    else:
      # We're past the end of the summary.
      # Additions now contribute to the description.
      state.description.lines.append(line_info.remaining_raw)
  else:
    state.summary.permitted = False

  if state.section.new and state.section.format == Formats.RST:
    # The current line starts with an RST directive, e.g. ":param arg:".
    directive = _get_directive(line_info)
    directive_tokens = directive.split()  # pytype: disable=attribute-error
    if state.section.title == Sections.ARGS:
      name = directive_tokens[-1]
      arg = _get_or_create_arg_by_name(state, name)
      if len(directive_tokens) == 3:
        # A param directive of the form ":param type arg:".
        arg.type.lines.append(directive_tokens[1])
      state.current_arg = arg
    elif state.section.title == Sections.TYPE:
      name = directive_tokens[-1]
      arg = _get_or_create_arg_by_name(state, name)
      state.current_arg = arg

  if (state.section.format == Formats.NUMPY and
      _line_is_hyphens(line_info.remaining)):
    # Skip this all-hyphens line, which is part of the numpy section header.
    return

  if state.section.title == Sections.ARGS:
    if state.section.format == Formats.GOOGLE:
      _consume_google_args_line(line_info, state)
    elif state.section.format == Formats.RST:
      state.current_arg.description.lines.append(line_info.remaining.strip())
    elif state.section.format == Formats.NUMPY:
      line_stripped = line_info.remaining.strip()
      if _is_arg_name(line_stripped):
        # Token on its own line can either be the last word of the description
        # of the previous arg, or a new arg. TODO: Whitespace can distinguish.
        arg = _get_or_create_arg_by_name(state, line_stripped)
        state.current_arg = arg
      elif ':' in line_stripped:
        possible_args, type_data = line_stripped.split(':', 1)
        arg_names = _as_arg_names(possible_args)  # re.split(' |,', s)
        if arg_names:
          for arg_name in arg_names:
            arg = _get_or_create_arg_by_name(state, arg_name)
            arg.type.lines.append(type_data)
            state.current_arg = arg  # TODO(dbieber): Multiple current args.
        else:  # Just an ordinary line.
          if state.current_arg:
            state.current_arg.description.lines.append(
                line_info.remaining.strip())
          else:
            # TODO(dbieber): If not a blank line, add it to the description.
            pass
      else:  # Just an ordinary line.
        if state.current_arg:
          state.current_arg.description.lines.append(
              line_info.remaining.strip())
        else:
          # TODO(dbieber): If not a blank line, add it to the description.
          pass

  elif state.section.title == Sections.RETURNS:
    state.returns.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.YIELDS:
    state.yields.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.RAISES:
    state.raises.lines.append(line_info.remaining.strip())
  elif state.section.title == Sections.TYPE:
    if state.section.format == Formats.RST:
      assert state.current_arg is not None
      state.current_arg.type.lines.append(line_info.remaining.strip())
    else:
      pass


def _create_line_info(line, next_line):
  """Returns information about the current and next line of the docstring."""
  line_info = Namespace()  # TODO(dbieber): Switch to an explicit class.
  line_info.line = line
  line_info.stripped = line.strip()
  line_info.remaining_raw = line_info.line
  line_info.remaining = line_info.stripped
  line_info.indentation = len(line) - len(line.lstrip())
  # TODO(dbieber): If next_line is blank, use the next non-blank line.
  line_info.next.line = next_line
  next_line_exists = next_line is not None
  line_info.next.stripped = next_line.strip() if next_line_exists else None
  line_info.next.indentation = (
      len(next_line) - len(next_line.lstrip()) if next_line_exists else None)
  # Note: This counts all whitespace equally.
  return line_info


def _update_section_state(line_info, state):
  """Uses line_info to determine the current section of the docstring.

  Updates state and line_info.remaining.

  Args:
    line_info: Information about the current line.
    state: The state of the parser.
  """
  section_updated = False

  google_section_permitted = _google_section_permitted(line_info, state)
  google_section = google_section_permitted and _google_section(line_info)
  if google_section:
    state.section.format = Formats.GOOGLE
    state.section.title = google_section
    line_info.remaining = _get_after_google_header(line_info)
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  rst_section = _rst_section(line_info)
  if rst_section:
    state.section.format = Formats.RST
    state.section.title = rst_section
    line_info.remaining = _get_after_directive(line_info)
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  numpy_section = _numpy_section(line_info)
  if numpy_section:
    state.section.format = Formats.NUMPY
    state.section.title = numpy_section
    line_info.remaining = ''
    line_info.remaining_raw = line_info.remaining
    section_updated = True

  if section_updated:
    state.section.new = True
    state.section.indentation = line_info.indentation
    state.section.line1_indentation = line_info.next.indentation
  else:
    state.section.new = False


def _google_section_permitted(line_info, state):
  """Returns whether a new google section is permitted to start here.

  Q: Why might a new Google section not be allowed?
  A: If we're in the middle of a Google "Args" section, then lines that start
  "param:" will usually be a new arg, rather than a new section.
  We use whitespace to determine when the Args section has actually ended.

  A Google section ends when either:
  - A new google section begins at either
    - indentation less than indentation of line 1 of the previous section
    - or <= indentation of the previous section
  - Or the docstring terminates.

  Args:
    line_info: Information about the current line.
    state: The state of the parser.
  Returns:
    True or False, indicating whether a new Google section is permitted at the
    current line.
  """
  if state.section.indentation is None:  # We're not in a section yet.
    return True
  return (line_info.indentation <= state.section.indentation
          or line_info.indentation < state.section.line1_indentation)


def _matches_section_title(title, section_title):
  """Returns whether title is a match for a specific section_title.

  Example:
    _matches_section_title('Yields', 'yield') == True

  Args:
    title: The title to check for matching.
    section_title: A specific known section title to check against.
  """
  title = title.lower()
  section_title = section_title.lower()
  return section_title in (title, title[:-1])  # Supports plurals / some typos.


def _matches_section(title, section):
  """Returns whether title is a match any known title for a specific section.

  Example:
    _matches_section_title('Yields', Sections.YIELDS) == True
    _matches_section_title('param', Sections.Args) == True

  Args:
    title: The title to check for matching.
    section: A specific section to check all possible titles for.
  Returns:
    True or False, indicating whether title is a match for the specified
    section.
  """
  for section_title in SECTION_TITLES[section]:
    if _matches_section_title(title, section_title):
      return True
  return False


def _section_from_possible_title(possible_title):
  """Returns a section matched by the possible title, or None if none match.

  Args:
    possible_title: A string that may be the title of a new section.
  Returns:
    A Section type if one matches, or None if no section type matches.
  """
  for section in SECTION_TITLES:
    if _matches_section(possible_title, section):
      return section
  return None


def _google_section(line_info):
  """Checks whether the current line is the start of a new Google-style section.

  This docstring is a Google-style docstring. Google-style sections look like
  this:

    Section Name:
      section body goes here

  Args:
    line_info: Information about the current line.
  Returns:
    A Section type if one matches, or None if no section type matches.
  """
  colon_index = line_info.remaining.find(':')
  possible_title = line_info.remaining[:colon_index]
  return _section_from_possible_title(possible_title)


def _get_after_google_header(line_info):
  """Gets the remainder of the line, after a Google header."""
  colon_index = line_info.remaining.find(':')
  return line_info.remaining[colon_index + 1:]


def _get_directive(line_info):
  """Gets a directive from the start of the line.

  If the line is ":param str foo: Description of foo", then
  _get_directive(line_info) returns "param str foo".

  Args:
    line_info: Information about the current line.
  Returns:
    The contents of a directive, or None if the line doesn't start with a
    directive.
  """
  if line_info.stripped.startswith(':'):
    return line_info.stripped.split(':', 2)[1]
  else:
    return None


def _get_after_directive(line_info):
  """Gets the remainder of the line, after a directive."""
  sections = line_info.stripped.split(':', 2)
  if len(sections) > 2:
    return sections[-1]
  else:
    return ''


def _rst_section(line_info):
  """Checks whether the current line is the start of a new RST-style section.

  RST uses directives to specify information. An RST directive, which we refer
  to as a section here, are surrounded with colons. For example, :param name:.

  Args:
    line_info: Information about the current line.
  Returns:
    A Section type if one matches, or None if no section type matches.
  """
  directive = _get_directive(line_info)
  if directive:
    possible_title = directive.split()[0]
    return _section_from_possible_title(possible_title)
  else:
    return None


def _line_is_hyphens(line):
  """Returns whether the line is entirely hyphens (and not blank)."""
  return line and not line.strip('-')


def _numpy_section(line_info):
  """Checks whether the current line is the start of a new numpy-style section.

  Numpy style sections are followed by a full line of hyphens, for example:

    Section Name
    ------------
    Section body goes here.

  Args:
    line_info: Information about the current line.
  Returns:
    A Section type if one matches, or None if no section type matches.
  """
  next_line_is_hyphens = _line_is_hyphens(line_info.next.stripped)
  if next_line_is_hyphens:
    possible_title = line_info.remaining
    return _section_from_possible_title(possible_title)
  else:
    return None
