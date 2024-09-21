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
"""Enables use of Python Fire as a "main" function (i.e. "python -m fire").

This allows using Fire with third-party libraries without modifying their code.
"""

import importlib
from importlib import util
import os
import sys

import fire

cli_string = """usage: python -m fire [module] [arg] ..."

Python Fire is a library for creating CLIs from absolutely any Python
object or program. To run Python Fire from the command line on an
existing Python file, it can be invoked with "python -m fire [module]"
and passed a Python module using module notation:

"python -m fire packageA.packageB.module"

or with a file path:

"python -m fire packageA/packageB/module.py" """


def import_from_file_path(path):
  """Performs a module import given the filename.

  Args:
    path (str): the path to the file to be imported.

  Raises:
    IOError: if the given file does not exist or importlib fails to load it.

  Returns:
    Tuple[ModuleType, str]: returns the imported module and the module name,
      usually extracted from the path itself.
  """

  if not os.path.exists(path):
    raise OSError('Given file path does not exist.')

  module_name = os.path.basename(path)

  spec = util.spec_from_file_location(module_name, path)

  if spec is None:
    raise OSError('Unable to load module from specified path.')

  module = util.module_from_spec(spec)  # pylint: disable=no-member
  spec.loader.exec_module(module)  # pytype: disable=attribute-error

  return module, module_name


def import_from_module_name(module_name):
  """Imports a module and returns it and its name."""
  module = importlib.import_module(module_name)
  return module, module_name


def import_module(module_or_filename):
  """Imports a given module or filename.

  If the module_or_filename exists in the file system and ends with .py, we
  attempt to import it. If that import fails, try to import it as a module.

  Args:
    module_or_filename (str): string name of path or module.

  Raises:
    ValueError: if the given file is invalid.
    IOError: if the file or module can not be found or imported.

  Returns:
    Tuple[ModuleType, str]: returns the imported module and the module name,
      usually extracted from the path itself.
  """

  if os.path.exists(module_or_filename):
    # importlib.util.spec_from_file_location requires .py
    if not module_or_filename.endswith('.py'):
      try:  # try as module instead
        return import_from_module_name(module_or_filename)
      except ImportError:
        raise ValueError('Fire can only be called on .py files.')

    return import_from_file_path(module_or_filename)

  if os.path.sep in module_or_filename:  # Use / to detect if it was a filename.
    raise OSError('Fire was passed a filename which could not be found.')

  return import_from_module_name(module_or_filename)  # Assume it's a module.


def main(args):
  """Entrypoint for fire when invoked as a module with python -m fire."""

  if len(args) < 2:
    print(cli_string)
    sys.exit(1)

  module_or_filename = args[1]
  module, module_name = import_module(module_or_filename)

  fire.Fire(module, name=module_name, command=args[2:])


if __name__ == '__main__':
  main(sys.argv)
