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

"""Fuzz tests for the docstring parser module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import docstrings
from fire import testutils

from hypothesis import example
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st


class DocstringsFuzzTest(testutils.BaseTestCase):

  @settings(max_examples=1000, deadline=1000)
  @given(st.text(min_size=1))
  @example('This is a one-line docstring.')
  def test_fuzz_parse(self, value):
    docstrings.parse(value)


if __name__ == '__main__':
  testutils.main()
