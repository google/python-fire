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

"""Tests for the calculator_tools module."""

from fire import testutils
from examples.calculator_tools import calculator_tools


class CalculatorToolsTest(testutils.BaseTestCase):

  def testCalculatorTools(self):
    # add
    self.assertEqual(calculator_tools.add(2, 3), 5)

    # subtract
    self.assertEqual(calculator_tools.subtract(10, 4), 6)

    # multiply
    self.assertEqual(calculator_tools.multiply(5, 2), 10)

    # divide
    self.assertEqual(calculator_tools.divide(20, 5), 4)

    # division by zero
    with self.assertRaises(ZeroDivisionError):
      calculator_tools.divide(10, 0)


if __name__ == '__main__':
  testutils.main()
