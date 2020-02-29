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

"""Tests for the cipher module."""

from fire import testutils

from examples.cipher import cipher


class CipherTest(testutils.BaseTestCase):

  def testCipher(self):
    self.assertEqual(cipher.rot13('Hello world!'), 'Uryyb jbeyq!')
    self.assertEqual(cipher.caesar_encode(13, 'Hello world!'), 'Uryyb jbeyq!')
    self.assertEqual(cipher.caesar_decode(13, 'Uryyb jbeyq!'), 'Hello world!')

    self.assertEqual(cipher.caesar_encode(1, 'Hello world!'), 'Ifmmp xpsme!')
    self.assertEqual(cipher.caesar_decode(1, 'Ifmmp xpsme!'), 'Hello world!')


if __name__ == '__main__':
  testutils.main()
