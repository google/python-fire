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

"""Tests for the url_tools module."""

from fire import testutils
from examples.url_tools import url_tools


class UrlToolsTest(testutils.BaseTestCase):

  def testEncodeDecode(self):
    encoded = url_tools.encode("Hello world!")
    self.assertEqual(encoded, "Hello%20world%21")

    decoded = url_tools.decode(encoded)
    self.assertEqual(decoded, "Hello world!")

  def testDomain(self):
    self.assertEqual(
        url_tools.domain("https://google.com/search?q=fire"),
        "google.com"
    )


if __name__ == "__main__":
  testutils.main()
