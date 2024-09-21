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

"""Fuzz tests for the parser module."""

from fire import parser
from fire import testutils
from hypothesis import example
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
import Levenshtein


class ParserFuzzTest(testutils.BaseTestCase):

  @settings(max_examples=10000)
  @given(st.text(min_size=1))
  @example('True')
  @example(r'"test\t\t\a\\a"')
  @example(r' "test\t\t\a\\a"   ')
  @example('"(1, 2)"')
  @example('(1, 2)')
  @example('(1,                   2)')
  @example('(1,       2) ')
  @example('a,b,c,d')
  @example('(a,b,c,d)')
  @example('[a,b,c,d]')
  @example('{a,b,c,d}')
  @example('test:(a,b,c,d)')
  @example('{test:(a,b,c,d)}')
  @example('{test:a,b,c,d}')
  @example('{test:a,b:(c,d)}')  # Note: Edit distance may be high for dicts.
  @example('0,')
  @example('#')
  @example('A#00000')  # Note: '#'' is treated as a comment.
  @example('\x80')  # Note: Causes UnicodeDecodeError.
  @example(100 * '[' + '0')  # Note: Causes MemoryError.
  @example('\r\r\r\r1\r\r')
  def testDefaultParseValueFuzz(self, value):
    try:
      result = parser.DefaultParseValue(value)
    except TypeError:
      # It's OK to get a TypeError if the string has the null character.
      if '\x00' in value:
        return
      raise
    except MemoryError:
      if len(value) > 100:
        # This is not what we're testing.
        return
      raise

    try:
      uvalue = str(value)
      uresult = str(result)
    except UnicodeDecodeError:
      # This is not what we're testing.
      return

    # Check that the parsed value doesn't differ too much from the input.
    distance = Levenshtein.distance(uresult, uvalue)
    max_distance = (
        2 +  # Quotes or parenthesis can be implicit.
        sum(c.isspace() for c in value) +
        value.count('"') + value.count("'") +
        3 * (value.count(',') + 1) +  # 'a,' can expand to "'a', "
        3 * (value.count(':')) +  # 'a:' can expand to "'a': "
        2 * value.count('\\'))
    if '#' in value:
      max_distance += len(value) - value.index('#')

    if not isinstance(result, str):
      max_distance += value.count('0')  # Leading 0s are stripped.

    # Note: We don't check distance for dicts since item order can be changed.
    if '{' not in value:
      self.assertLessEqual(distance, max_distance,
                           (distance, max_distance, uvalue, uresult))


if __name__ == '__main__':
  testutils.main()
