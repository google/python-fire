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

"""This module enables interactive mode in Python Fire.

It uses IPython as an optional dependency. When IPython is installed, the
interactive flag will use IPython's REPL. When IPython is not installed, the
interactive flag will start a Python REPL with the builtin `code` module's
InteractiveConsole class.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect


def Embed(variables, verbose=False):
  """Drops into a Python REPL with variables available as local variables.

  Args:
    variables: A dict of variables to make available. Keys are variable names.
        Values are variable values.
    verbose: Whether to include 'hidden' members, those keys starting with _.
  """
  print(_AvailableString(variables, verbose))

  try:
    _EmbedIPython(variables)
  except ImportError:
    _EmbedCode(variables)


def _AvailableString(variables, verbose=False):
  """Returns a string describing what objects are available in the Python REPL.

  Args:
    variables: A dict of the object to be available in the REPL.
    verbose: Whether to include 'hidden' members, those keys starting with _.
  Returns:
    A string fit for printing at the start of the REPL, indicating what objects
    are available for the user to use.
  """
  modules = []
  other = []
  for name, value in variables.items():
    if not verbose and name.startswith('_'):
      continue
    if '-' in name or '/' in name:
      continue

    if inspect.ismodule(value):
      modules.append(name)
    else:
      other.append(name)

  lists = [
      ('Modules', modules),
      ('Objects', other)]
  liststrs = []
  for name, varlist in lists:
    if varlist:
      liststrs.append(
          '{name}: {items}'.format(name=name, items=', '.join(sorted(varlist))))

  return (
      'Fire is starting a Python REPL with the following objects:\n'
      '{liststrs}\n'
  ).format(liststrs='\n'.join(liststrs))


def _EmbedIPython(variables, argv=None):
  """Drops into an IPython REPL with variables available for use.

  Args:
    variables: A dict of variables to make available. Keys are variable names.
        Values are variable values.
    argv: The argv to use for starting ipython. Defaults to an empty list.
  """
  import IPython  # pylint: disable=import-outside-toplevel,g-import-not-at-top
  argv = argv or []
  IPython.start_ipython(argv=argv, user_ns=variables)


def _EmbedCode(variables):
  import code  # pylint: disable=import-outside-toplevel,g-import-not-at-top
  code.InteractiveConsole(variables).interact()
