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

import termcolor


def Indent(text, spaces=2):
  lines = text.split('\n')
  return '\n'.join(
      ' ' * spaces + line if line else line
      for line in lines)


def Bold(text):
  return termcolor.colored(text, attrs=['bold'])


def Underline(text):
  return termcolor.colored(text, attrs=['underline'])

