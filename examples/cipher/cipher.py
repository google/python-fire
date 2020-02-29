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

"""The Caesar Shift Cipher example Fire CLI.

This module demonstrates the use of Fire without specifying a target component.
Notice how the call to Fire() in the main method doesn't indicate a component.
So, all local and global variables (including all functions defined in the
module) are made available as part of the Fire CLI.

Example usage:
cipher rot13 'Hello world!'  # Uryyb jbeyq!
cipher rot13 'Uryyb jbeyq!'  # Hello world!
cipher caesar-encode 1 'Hello world!'  # Ifmmp xpsme!
cipher caesar-decode 1 'Ifmmp xpsme!'  # Hello world!
"""

import fire


def caesar_encode(n=0, text=''):
  return ''.join(
      _caesar_shift_char(n, char)
      for char in text
  )


def caesar_decode(n=0, text=''):
  return caesar_encode(-n, text)


def rot13(text):
  return caesar_encode(13, text)


def _caesar_shift_char(n=0, char=' '):
  if not char.isalpha():
    return char
  if char.isupper():
    return chr((ord(char) - ord('A') + n) % 26 + ord('A'))
  return chr((ord(char) - ord('a') + n) % 26 + ord('a'))


def main():
  fire.Fire(name='cipher')

if __name__ == '__main__':
  main()
