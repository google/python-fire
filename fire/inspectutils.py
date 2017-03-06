# Copyright (C) 2017 Google Inc.
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

"""Inspection utility functions for Python Fire."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect

import IPython
import six


def _GetArgSpecFnInfo(fn):
  """Gives information pertaining to computing the ArgSpec of fn.

  Determines if the first arg is supplied automatically when fn is called.
  This arg will be supplied automatically if fn is a bound method or a class
  with an __init__ method.

  Also returns the function who's ArgSpec should be used for determining the
  calling parameters for fn. This may be different from fn itself if fn is a
  class with an __init__ method.

  Args:
    fn: The function or class of interest.
  Returns:
    A tuple with the following two items:
      fn: The function to use for determing the arg spec of this function.
      skip_arg: Whether the first argument will be supplied automatically, and
        hence should be skipped when supplying args from a Fire command.
  """
  skip_arg = False
  if inspect.isclass(fn):
    # If the function is a class, we try to use it's init method.
    skip_arg = True
    if six.PY2 and hasattr(fn, '__init__'):
      fn = fn.__init__
  else:
    # If the function is a bound method, we skip the `self` argument.
    is_method = inspect.ismethod(fn)
    skip_arg = is_method and fn.__self__ is not None

  return fn, skip_arg


def GetArgSpec(fn):
  """Returns information about the function signature.

  Args:
    fn: The function to analyze.
  Returns:
    A named tuple of type inspect.ArgSpec with the following fields:
      args: A list of the argument names accepted by the function.
      varargs: The name of the *varargs argument or None if there isn't one.
      keywords: The name of the **kwargs argument or None if there isn't one.
      defaults: A tuple of the defaults for the arguments that accept defaults.
  """
  fn, skip_arg = _GetArgSpecFnInfo(fn)

  try:

    if six.PY2:
      argspec = inspect.getargspec(fn)
      keywords = argspec.keywords
    else:
      argspec = inspect.getfullargspec(fn)
      keywords = argspec.varkw

    args = argspec.args
    defaults = argspec.defaults or ()
    varargs = argspec.varargs

  except TypeError:
    args = []
    defaults = ()
    # If we can't get the argspec, how do we know if the fn should take args?
    # 1. If it's a builtin, it can take args.
    # 2. If it's an implicit __init__ function (a 'slot wrapper'), take no args.
    # Are there other cases?
    varargs = 'vars' if inspect.isbuiltin(fn) else None
    keywords = 'kwargs' if inspect.isbuiltin(fn) else None

  if skip_arg:
    args = args[1:]  # Remove self.

  return inspect.ArgSpec(
      args=args,
      varargs=varargs,
      keywords=keywords,
      defaults=defaults)


def Info(component):
  """Returns a dict with information about the given component.

  The dict will have at least some of the following fields.
    type_name: The type of `component`.
    string_form: A string representation of `component`.
    file: The file in which `component` is defined.
    line: The line number at which `component` is defined.
    docstring: The docstring of `component`.
    init_docstring: The init docstring of `component`.
    class_docstring: The class docstring of `component`.
    call_docstring: The call docstring of `component`.
    length: The length of `component`.

  Args:
    component: The component to analyze.
  Returns:
    A dict with information about the component.
  """
  inspector = IPython.core.oinspect.Inspector()
  info = inspector.info(component)

  try:
    unused_code, lineindex = inspect.findsource(component)
    info['line'] = lineindex + 1
  except (TypeError, IOError):
    info['line'] = None

  return info
