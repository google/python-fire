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

"""Provides parsing functionality used by Python Fire."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import ast


def CreateParser():
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('--verbose', '-v', action='store_true')
  parser.add_argument('--interactive', '-i', action='store_true')
  parser.add_argument('--separator', default='-')
  parser.add_argument('--completion', nargs='?', const='bash', type=str)
  parser.add_argument('--help', '-h', action='store_true')
  parser.add_argument('--trace', '-t', action='store_true')
  # TODO(dbieber): Consider allowing name to be passed as an argument.
  return parser


def SeparateFlagArgs(args):
  """Splits a list of args into those for Flags and those for Fire.

  If an isolated '--' arg is not present in the arg list, then all of the args
  are for Fire. If there is an isolated '--', then the args after the final '--'
  are flag args, and the rest of the args are fire args.

  Args:
    args: The list of arguments received by the Fire command.
  Returns:
    A tuple with the Fire args (a list), followed by the Flag args (a list).
  """
  if '--' in args:
    separator_index = len(args) - 1 - args[::-1].index('--')  # index of last --
    flag_args = args[separator_index + 1:]
    args = args[:separator_index]
    return args, flag_args
  return args, []


def DefaultParseValue(value):
  """The default argument parsing function used by Fire CLIs.

  If the value is made of only Python literals and containers, then the value
  is parsed as it's Python value. Otherwise, provided the value contains no
  quote, escape, or parenthetical characters, the value is treated as a string.

  Args:
    value: A string from the command line to be parsed for use in a Fire CLI.
  Returns:
    The parsed value, of the type determined most appropriate.
  """
  # Note: _LiteralEval will treat '#' as the start of a comment.
  try:
    return _LiteralEval(value)
  except (SyntaxError, ValueError):
    # If _LiteralEval can't parse the value, treat it as a string.
    return value

def _LiteralEval(value):
  """Parse value as a Python literal, or container of containers and literals.

  First the AST of the value is updated so that bare-words are turned into
  strings. Then the resulting AST is evaluated as a literal or container of
  only containers and literals.

  This allows for the YAML-like syntax {a: b} to represent the dict {'a': 'b'}

  Args:
    value: A string to be parsed as a literal or container of containers and
      literals.
  Returns:
    The Python value representing the value arg.
  Raises:
    ValueError: If the value is not an expression with only containers and
      literals.
    SyntaxError: If the value string has a syntax error.
  """

  ptr = 0   # Represents the current position in 'value'
  brace_stack = []   # Keeps track of curly braces

  # Set of characters that will help distinguish between two container elements
  delimiter = {',', ']', '}', ')', ' '}

  while ptr < len(value):
    if value[ptr] in {'{', '[', '('}:
      # Beginning of container encountered
      if value[ptr] == '{':
        if not brace_stack:
          # Potential dictionary encountered, add colon as delimiter
          delimiter.add(':')
        brace_stack.append('{')

      ptr += 1
    elif value[ptr] in {"'", '"'}:
      # Beginning of string encountered
      if value[ptr: ptr + 3] in {"'''", '"""'}:
        # Triple quotes for strings
        left = ptr
        right = ptr + 3

        # Search for the ending triple quotes
        while (right < len(value) and
               value[right: right + 3] != value[left: left + 3]):
          right += 1

        ptr = right + 3
      else:
        # Single quotes for strings
        left = ptr
        right = ptr + 1

        # Search for the ending single quote
        while (right < len(value) and
               value[right] != value[left]):
          right += 1

        ptr = right + 1

      # Skip all delimiters occuring after this
      while ptr < len(value) and value[ptr] in delimiter:
        if value[ptr] == '}' and brace_stack:
          brace_stack.pop()
          if not brace_stack:
            # All potential dictionaries exited,
            # remove colon (:) from delimiter
            delimiter.remove(':')

        ptr += 1
    else:
      # Literal encountered
      left = ptr
      right = ptr + 1

      delimiter.remove(' ') # Don't consider space as a delimiter in strings

      while right < len(value) and value[right] not in delimiter:
        right += 1

      delimiter.add(' ')

      element = value[left: right]  # Single element identified

      # If the element is of type string or ellipsis,
      # put quotes around it
      if isinstance(_SingleLiteralEval(element), str) or element == "...":
        value = _InsertQuotes(value, left, right)
        right += 2

      ptr = right

      # Skip all delimiters occuring after this
      while ptr < len(value) and value[ptr] in delimiter:
        if value[ptr] == '}' and brace_stack:
          brace_stack.pop()
          if not brace_stack:
            # All potential dictionaries exited,
            # remove colon (:) from delimiter
            delimiter.remove(':')

        ptr += 1

  root = ast.parse(value, mode='eval')

  return ast.literal_eval(root)


def _SingleLiteralEval(value):
  """Parse value as a Python literal only.

  Args:
    value: A string to be parsed as a literal only.
  Returns:
    The Python value representing the value arg.
  Raises:
    ValueError: If the value is not an expression with only containers and
      literals.
    SyntaxError: If the value string has a syntax error.
  """

  try:
    return ast.literal_eval(value)
  except (SyntaxError, ValueError):
    # If _SingleLiteralEval can't parse the value, treat it as a string.
    return value


def _InsertQuotes(string, left_index, right_index):
  """Insert quotes in the passed string.

  Args:
    string: A string in which quotes will be inserted.
    left_index: An integer representing the index where
      starting quote will be inserted.
    right_index: An integer representing the index where
      closing quote will be inserted.
  Returns:
    The modified string with quotes inserted at left_index and right_index.
  """
  return (string[:left_index] + "'" +
          string[left_index: right_index] + "'" +
          string[right_index:])
