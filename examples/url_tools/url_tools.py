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

"""URL utilities Fire CLI.

This module demonstrates using Fire to expose URL helper functions.
Fire() is invoked without a target component, so all functions are available
as CLI commands.

Example usage:
  url_tools encode "Hello world!"
  url_tools decode "Hello%20world%21"
  url_tools domain "https://google.com/search?q=fire"
"""

import fire
from urllib.parse import quote, unquote, urlparse


def encode(text=''):
  """URL-encode the given text."""
  return quote(text)


def decode(text=''):
  """URL-decode the given text."""
  return unquote(text)


def domain(url=''):
  """Return the domain name from the given URL."""
  return urlparse(url).netloc


def main():
  fire.Fire(name='url_tools')


if __name__ == "__main__":
  main()
