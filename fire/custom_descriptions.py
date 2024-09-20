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

"""Custom descriptions and summaries for the builtin types.

The docstrings for objects of primitive types reflect the type of the object,
rather than the object itself. For example, the docstring for any dict is this:

> print({'key': 'value'}.__doc__)
dict() -> new empty dictionary
dict(mapping) -> new dictionary initialized from a mapping object's
    (key, value) pairs
dict(iterable) -> new dictionary initialized as if via:
    d = {}
    for k, v in iterable:
        d[k] = v
dict(**kwargs) -> new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)

As you can see, this docstring is more pertinent to the function `dict` and
would be suitable as the result of `dict.__doc__`, but is wholely unsuitable
as a description for the dict `{'key': 'value'}`.

This modules aims to resolve that problem, providing custom summaries and
descriptions for primitive typed values.
"""

from fire import formatting

TWO_DOUBLE_QUOTES = '""'
STRING_DESC_PREFIX = 'The string '


def NeedsCustomDescription(component):
  """Whether the component should use a custom description and summary.

  Components of primitive type, such as ints, floats, dicts, lists, and others
  have messy builtin docstrings. These are inappropriate for display as
  descriptions and summaries in a CLI. This function determines whether the
  provided component has one of these docstrings.

  Note that an object such as `int` has the same docstring as an int like `3`.
  The docstring is OK for `int`, but is inappropriate as a docstring for `3`.

  Args:
    component: The component of interest.
  Returns:
    Whether the component should use a custom description and summary.
  """
  type_ = type(component)
  if (
      type_ in (str, int, bytes)
      or type_ in (float, complex, bool)
      or type_ in (dict, tuple, list, set, frozenset)
  ):
    return True
  return False


def GetStringTypeSummary(obj, available_space, line_length):
  """Returns a custom summary for string type objects.

  This function constructs a summary for string type objects by double quoting
  the string value. The double quoted string value will be potentially truncated
  with ellipsis depending on whether it has enough space available to show the
  full string value.

  Args:
    obj: The object to generate summary for.
    available_space: Number of character spaces available.
    line_length: The full width of the terminal, default is 80.

  Returns:
    A summary for the input object.
  """
  if len(obj) + len(TWO_DOUBLE_QUOTES) <= available_space:
    content = obj
  else:
    additional_len_needed = len(TWO_DOUBLE_QUOTES) + len(formatting.ELLIPSIS)
    if available_space < additional_len_needed:
      available_space = line_length
    content = formatting.EllipsisTruncate(
        obj, available_space - len(TWO_DOUBLE_QUOTES), line_length)
  return formatting.DoubleQuote(content)


def GetStringTypeDescription(obj, available_space, line_length):
  """Returns the predefined description for string obj.

  This function constructs a description for string type objects in the format
  of 'The string "<string_value>"'. <string_value> could be potentially
  truncated depending on whether it has enough space available to show the full
  string value.

  Args:
    obj: The object to generate description for.
    available_space: Number of character spaces available.
    line_length: The full width of the terminal, default if 80.

  Returns:
    A description for input object.
  """
  additional_len_needed = len(STRING_DESC_PREFIX) + len(
      TWO_DOUBLE_QUOTES) + len(formatting.ELLIPSIS)
  if available_space < additional_len_needed:
    available_space = line_length

  return STRING_DESC_PREFIX + formatting.DoubleQuote(
      formatting.EllipsisTruncate(
          obj, available_space - len(STRING_DESC_PREFIX) -
          len(TWO_DOUBLE_QUOTES), line_length))


CUSTOM_DESC_SUM_FN_DICT = {
    'str': (GetStringTypeSummary, GetStringTypeDescription),
    'unicode': (GetStringTypeSummary, GetStringTypeDescription),
}


def GetSummary(obj, available_space, line_length):
  obj_type_name = type(obj).__name__
  if obj_type_name in CUSTOM_DESC_SUM_FN_DICT:
    return CUSTOM_DESC_SUM_FN_DICT.get(obj_type_name)[0](obj, available_space,
                                                         line_length)
  return None


def GetDescription(obj, available_space, line_length):
  obj_type_name = type(obj).__name__
  if obj_type_name in CUSTOM_DESC_SUM_FN_DICT:
    return CUSTOM_DESC_SUM_FN_DICT.get(obj_type_name)[1](obj, available_space,
                                                         line_length)
  return None
