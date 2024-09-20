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

"""As a simple example of Python Fire, a Widget serves no clear purpose."""

import fire


class Widget(object):

  def whack(self, n=1):
    """Prints "whack!" n times."""
    return ' '.join('whack!' for _ in range(n))

  def bang(self, noise='bang'):
    """Makes a loud noise."""
    return f'{noise} bang!'


def main():
  fire.Fire(Widget(), name='widget')

if __name__ == '__main__':
  main()
