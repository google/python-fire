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

"""Formatting utilities for use in creating help text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import platform
import sys
import termcolor

ELLIPSIS = '...'

# Enable ANSI processing on Windows or disable entirely.
if sys.platform.startswith('win'):
  try:
    import colorama  # pylint: disable=g-import-not-at-top,  # pytype: disable=import-error
    HAS_COLORAMA = True
  except ImportError:
    HAS_COLORAMA = False

  if HAS_COLORAMA:
    SHOULD_WRAP = True
    if sys.stdout.isatty() and platform.release() == '10':
      # Enables native ANSI sequences in console.
      # Windows 10, 2016, and 2019 only.
      import ctypes  # pylint: disable=g-import-not-at-top
      import subprocess  # pylint: disable=g-import-not-at-top

      SHOULD_WRAP = False
      KERNEL32 = ctypes.windll.kernel32  # pytype: disable=module-attr
      ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x04
      OUT_HANDLE = KERNEL32.GetStdHandle(subprocess.STD_OUTPUT_HANDLE)  # pytype: disable=module-attr
      # GetConsoleMode fails if the terminal isn't native.
      MODE = ctypes.wintypes.DWORD()
      if KERNEL32.GetConsoleMode(OUT_HANDLE, ctypes.byref(MODE)) == 0:
        SHOULD_WRAP = True
      if not MODE.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
        if KERNEL32.SetConsoleMode(
            OUT_HANDLE, MODE.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
          # kernel32.SetConsoleMode to enable ANSI sequences failed
          SHOULD_WRAP = True
    colorama.init(wrap=SHOULD_WRAP)
  else:
    os.environ['ANSI_COLORS_DISABLED'] = '1'


def Indent(text, spaces=2):
  lines = text.split('\n')
  return '\n'.join(
      ' ' * spaces + line if line else line
      for line in lines)


def Bold(text):
  return termcolor.colored(text, attrs=['bold'])


def Underline(text):
  return termcolor.colored(text, attrs=['underline'])


def BoldUnderline(text):
  return Bold(Underline(text))


def WrappedJoin(items, separator=' | ', width=80):
  """Joins the items by the separator, wrapping lines at the given width."""
  lines = []
  current_line = ''
  for index, item in enumerate(items):
    is_final_item = index == len(items) - 1
    if is_final_item:
      if len(current_line) + len(item) <= width:
        current_line += item
      else:
        lines.append(current_line.rstrip())
        current_line = item
    else:
      if len(current_line) + len(item) + len(separator) <= width:
        current_line += item + separator
      else:
        lines.append(current_line.rstrip())
        current_line = item + separator

  lines.append(current_line)
  return lines


def Error(text):
  return termcolor.colored(text, color='red', attrs=['bold'])


def EllipsisTruncate(text, available_space, line_length):
  """Truncate text from the end with ellipsis."""
  if available_space < len(ELLIPSIS):
    available_space = line_length
  # No need to truncate
  if len(text) <= available_space:
    return text
  return text[:available_space - len(ELLIPSIS)] + ELLIPSIS


def EllipsisMiddleTruncate(text, available_space, line_length):
  """Truncates text from the middle with ellipsis."""
  if available_space < len(ELLIPSIS):
    available_space = line_length
  if len(text) < available_space:
    return text
  available_string_len = available_space - len(ELLIPSIS)
  first_half_len = int(available_string_len / 2)  # start from middle
  second_half_len = available_string_len - first_half_len
  return text[:first_half_len] + ELLIPSIS + text[-second_half_len:]


def DoubleQuote(text):
  return '"%s"' % text
