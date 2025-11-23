# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""String tools example Fire CLI.

This module demonstrates the use of Fire without specifying a target component.
By calling Fire() without arguments in main(), all functions defined in this
module become available as CLI commands.

Example usage:
  string_tools reverse "Hello World"
  string_tools uppercase "hello"
  string_tools count-words "Hello world from Fire"
"""

import fire


def reverse(text=''):
  """Return the reversed string."""
  return text[::-1]


def uppercase(text=''):
  """Return the text in uppercase."""
  return text.upper()


def count_words(text=''):
  """Return the number of words in the text."""
  return len(text.split())


def main():
  fire.Fire(name='string_tools')


if __name__ == '__main__':
  main()
