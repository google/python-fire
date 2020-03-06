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

# pylint: disable=invalid-name
"""Enables use of Python Fire as a "main" function (i.e. `python -m fire`).

This allows using Fire with third-party libraries without modifying their code.
"""

import importlib
import sys

import fire


def main(args):
  module_name = args[1]
  module = importlib.import_module(module_name)
  fire.Fire(module, name=module_name, command=args[2:])


if __name__ == '__main__':
  main(sys.argv)
