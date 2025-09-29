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

"""Tests for the parser module."""

from fire import parser
from fire import testutils


class ParserTest(testutils.BaseTestCase):

  def testCreateParser(self):
    self.assertIsNotNone(parser.CreateParser())

  def testSeparateFlagArgs(self):
    self.assertEqual(parser.SeparateFlagArgs([]), ([], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b']), (['a', 'b'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--']),
                     (['a', 'b'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c']),
                     (['a', 'b'], ['c']))
    self.assertEqual(parser.SeparateFlagArgs(['--']),
                     ([], []))
    self.assertEqual(parser.SeparateFlagArgs(['--', 'c', 'd']),
                     ([], ['c', 'd']))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', 'd']),
                     (['a', 'b'], ['c', 'd']))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', 'd', '--']),
                     (['a', 'b', '--', 'c', 'd'], []))
    self.assertEqual(parser.SeparateFlagArgs(['a', 'b', '--', 'c', '--', 'd']),
                     (['a', 'b', '--', 'c'], ['d']))

  def testDefaultParseValueStrings(self):
    self.assertEqual(parser.DefaultParseValue('hello'), 'hello')
    self.assertEqual(parser.DefaultParseValue('path/file.jpg'), 'path/file.jpg')
    self.assertEqual(parser.DefaultParseValue('hello world'), 'hello world')
    self.assertEqual(parser.DefaultParseValue('--flag'), '--flag')

  def testDefaultParseValueQuotedStrings(self):
    self.assertEqual(parser.DefaultParseValue("'hello'"), 'hello')
    self.assertEqual(parser.DefaultParseValue("'hello world'"), 'hello world')
    self.assertEqual(parser.DefaultParseValue("'--flag'"), '--flag')
    self.assertEqual(parser.DefaultParseValue('"hello"'), 'hello')
    self.assertEqual(parser.DefaultParseValue('"hello world"'), 'hello world')
    self.assertEqual(parser.DefaultParseValue('"--flag"'), '--flag')

  def testDefaultParseValueSpecialStrings(self):
    self.assertEqual(parser.DefaultParseValue('-'), '-')
    self.assertEqual(parser.DefaultParseValue('--'), '--')
    self.assertEqual(parser.DefaultParseValue('---'), '---')
    self.assertEqual(parser.DefaultParseValue('----'), '----')
    self.assertEqual(parser.DefaultParseValue('None'), None)
    self.assertEqual(parser.DefaultParseValue("'None'"), 'None')

  def testDefaultParseValueNumbers(self):
    self.assertEqual(parser.DefaultParseValue('23'), 23)
    self.assertEqual(parser.DefaultParseValue('-23'), -23)
    self.assertEqual(parser.DefaultParseValue('23.0'), 23.0)
    self.assertIsInstance(parser.DefaultParseValue('23'), int)
    self.assertIsInstance(parser.DefaultParseValue('23.0'), float)
    self.assertEqual(parser.DefaultParseValue('23.5'), 23.5)
    self.assertEqual(parser.DefaultParseValue('-23.5'), -23.5)

  def testDefaultParseValueStringNumbers(self):
    self.assertEqual(parser.DefaultParseValue("'23'"), '23')
    self.assertEqual(parser.DefaultParseValue("'23.0'"), '23.0')
    self.assertEqual(parser.DefaultParseValue("'23.5'"), '23.5')
    self.assertEqual(parser.DefaultParseValue('"23"'), '23')
    self.assertEqual(parser.DefaultParseValue('"23.0"'), '23.0')
    self.assertEqual(parser.DefaultParseValue('"23.5"'), '23.5')

  def testDefaultParseValueQuotedStringNumbers(self):
    self.assertEqual(parser.DefaultParseValue('"\'123\'"'), "'123'")

  def testDefaultParseValueOtherNumbers(self):
    self.assertEqual(parser.DefaultParseValue('1e5'), 100000.0)

  def testDefaultParseValueLists(self):
    self.assertEqual(parser.DefaultParseValue('[1, 2, 3]'), [1, 2, 3])
    self.assertEqual(parser.DefaultParseValue('[1, "2", 3]'), [1, '2', 3])
    self.assertEqual(parser.DefaultParseValue('[1, \'"2"\', 3]'), [1, '"2"', 3])
    self.assertEqual(parser.DefaultParseValue(
        '[1, "hello", 3]'), [1, 'hello', 3])

  def testDefaultParseValueBareWordsLists(self):
    self.assertEqual(parser.DefaultParseValue('[one, 2, "3"]'), ['one', 2, '3'])

  def testDefaultParseValueDict(self):
    self.assertEqual(
        parser.DefaultParseValue('{"abc": 5, "123": 1}'), {'abc': 5, '123': 1})

  def testDefaultParseValueNone(self):
    self.assertEqual(parser.DefaultParseValue('None'), None)

  def testDefaultParseValueBool(self):
    self.assertEqual(parser.DefaultParseValue('True'), True)
    self.assertEqual(parser.DefaultParseValue('False'), False)

  def testDefaultParseValueBareWordsTuple(self):
    self.assertEqual(parser.DefaultParseValue('(one, 2, "3")'), ('one', 2, '3'))
    self.assertEqual(parser.DefaultParseValue('one, "2", 3'), ('one', '2', 3))

  def testDefaultParseValueNestedContainers(self):
    self.assertEqual(
        parser.DefaultParseValue(
            '[(A, 2, "3"), 5, {alpha: 10.2, beta: "cat"}]'),
        [('A', 2, '3'), 5, {'alpha': 10.2, 'beta': 'cat'}])

  def testDefaultParseValueComments(self):
    self.assertEqual(parser.DefaultParseValue('"0#comments"'), '0#comments')
    # Comments are stripped. This behavior may change in the future.
    self.assertEqual(parser.DefaultParseValue('0#comments'), 0)

  def testDefaultParseValueBadLiteral(self):
    # If it can't be parsed, we treat it as a string. This behavior may change.
    self.assertEqual(
        parser.DefaultParseValue('[(A, 2, "3"), 5'), '[(A, 2, "3"), 5')
    self.assertEqual(parser.DefaultParseValue('x=10'), 'x=10')

  def testDefaultParseValueSyntaxError(self):
    # If it can't be parsed, we treat it as a string.
    self.assertEqual(parser.DefaultParseValue('"'), '"')

  def testDefaultParseValueIgnoreBinOp(self):
    self.assertEqual(parser.DefaultParseValue('2017-10-10'), '2017-10-10')
    self.assertEqual(parser.DefaultParseValue('1+1'), '1+1')

if __name__ == '__main__':
  testutils.main()
