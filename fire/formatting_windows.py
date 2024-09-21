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

"""This module is used for enabling formatting on Windows."""

import ctypes
import os
import platform
import subprocess
import sys

try:
  import colorama  # pylint: disable=g-import-not-at-top,  # pytype: disable=import-error
  HAS_COLORAMA = True
except ImportError:
  HAS_COLORAMA = False


def initialize_or_disable():
  """Enables ANSI processing on Windows or disables it as needed."""
  if HAS_COLORAMA:
    wrap = True
    if (hasattr(sys.stdout, 'isatty')
        and sys.stdout.isatty()
        and platform.release() == '10'):
      # Enables native ANSI sequences in console.
      # Windows 10, 2016, and 2019 only.

      wrap = False
      kernel32 = ctypes.windll.kernel32  # pytype: disable=module-attr
      enable_virtual_terminal_processing = 0x04
      out_handle = kernel32.GetStdHandle(subprocess.STD_OUTPUT_HANDLE)  # pylint: disable=line-too-long,  # pytype: disable=module-attr
      # GetConsoleMode fails if the terminal isn't native.
      mode = ctypes.wintypes.DWORD()
      if kernel32.GetConsoleMode(out_handle, ctypes.byref(mode)) == 0:
        wrap = True
      if not mode.value & enable_virtual_terminal_processing:
        if kernel32.SetConsoleMode(
            out_handle, mode.value | enable_virtual_terminal_processing) == 0:
          # kernel32.SetConsoleMode to enable ANSI sequences failed
          wrap = True
    colorama.init(wrap=wrap)
  else:
    os.environ['ANSI_COLORS_DISABLED'] = '1'

if sys.platform.startswith('win'):
  initialize_or_disable()
