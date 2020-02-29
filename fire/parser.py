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
  root = ast.parse(value, mode='eval')
  if isinstance(root.body, ast.BinOp):  # pytype: disable=attribute-error
    raise ValueError(value)

  for node in ast.walk(root):
    for field, child in ast.iter_fields(node):
      if isinstance(child, list):
        for index, subchild in enumerate(child):
          if isinstance(subchild, ast.Name):
            child[index] = _Replacement(subchild)

      elif isinstance(child, ast.Name):
        replacement = _Replacement(child)
        node.__setattr__(field, replacement)

  # ast.literal_eval supports the following types:
  # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
  # (bytes and set literals only starting with Python 3.2)
  return ast.literal_eval(root)


def _Replacement(node):
  """Returns a node to use in place of the supplied node in the AST.

  Args:
    node: A node of type Name. Could be a variable, or builtin constant.
  Returns:
    A node to use in place of the supplied Node. Either the same node, or a
    String node whose value matches the Name node's id.
  """
  value = node.id
  # These are the only builtin constants supported by literal_eval.
  if value in ('True', 'False', 'None'):
    return node
  return ast.Str(value)
