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

"""Simple calculator example Fire CLI.

This module demonstrates the use of Fire without specifying a target component.
All functions become CLI commands when Fire() is invoked in main().

Example usage:
  calculator_tools add 2 3
  calculator_tools subtract 10 4
  calculator_tools multiply 5 6
  calculator_tools divide 20 5
"""

import fire


def add(a=0, b=0):
  """Return the sum of a and b."""
  return a + b


def subtract(a=0, b=0):
  """Return a - b."""
  return a - b


def multiply(a=0, b=0):
  """Return a * b."""
  return a * b


def divide(a=0, b=1):
  """Return a / b."""
  if b == 0:
    raise ZeroDivisionError("Cannot divide by zero.")
  return a / b


def main():
  fire.Fire(name='calculator_tools')


if __name__ == '__main__':
  main()
