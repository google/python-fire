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

"""Tests for custom description module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import custom_descriptions
from fire import testutils

LINE_LENGTH = 80


class CustomDescriptionTest(testutils.BaseTestCase):

  def test_string_type_summary_enough_space(self):
    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=80, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Test"')

  def test_string_type_summary_not_enough_space_truncated(self):
    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=5, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"..."')

  def test_string_type_summary_not_enough_space_new_line(self):
    component = 'Test'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=4, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Test"')

  def test_string_type_summary_not_enough_space_long_truncated(self):
    component = 'Lorem ipsum dolor sit amet'
    summary = custom_descriptions.GetSummary(
        obj=component, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual(summary, '"Lorem..."')

  def test_string_type_description_enough_space(self):
    component = 'Test'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=80, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Test"')

  def test_string_type_description_not_enough_space_truncated(self):
    component = 'Lorem ipsum dolor sit amet'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=20, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Lore..."')

  def test_string_type_description_not_enough_space_new_line(self):
    component = 'Lorem ipsum dolor sit amet'
    description = custom_descriptions.GetDescription(
        obj=component, available_space=10, line_length=LINE_LENGTH)
    self.assertEqual(description, 'The string "Lorem ipsum dolor sit amet"')


if __name__ == '__main__':
  testutils.main()
