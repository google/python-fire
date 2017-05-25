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

import six


class FullArgSpec(object):
  """The arguments of a function, as in Python 3's inspect.FullArgSpec."""

  def __init__(self, args=None, varargs=None, varkw=None, defaults=None,
               kwonlyargs=None, kwonlydefaults=None, annotations=None):
    """Constructs a FullArgSpec with each provided attribute, or the default.

    Args:
      args: A list of the argument names accepted by the function.
      varargs: The name of the *varargs argument or None if there isn't one.
      varkw: The name of the **kwargs argument or None if there isn't one.
      defaults: A tuple of the defaults for the arguments that accept defaults.
      kwonlyargs: A list of argument names that must be passed with a keyword.
      kwonlydefaults: A dictionary of keyword only arguments and their defaults.
      annotations: A dictionary of arguments and their annotated types.
    """
    self.args = args or []
    self.varargs = varargs
    self.varkw = varkw
    self.defaults = defaults or ()
    self.kwonlyargs = kwonlyargs or []
    self.kwonlydefaults = kwonlydefaults or {}
    self.annotations = annotations or {}


def _GetArgSpecInfo(fn):
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


def GetFullArgSpec(fn):
  """Returns a FullArgSpec describing the given callable."""

  fn, skip_arg = _GetArgSpecInfo(fn)

  try:
    if six.PY2:
      args, varargs, varkw, defaults = inspect.getargspec(fn)  # pylint: disable=deprecated-method
      kwonlyargs = kwonlydefaults = None
      annotations = getattr(fn, '__annotations__', None)
    else:
      (args, varargs, varkw, defaults,
       kwonlyargs, kwonlydefaults, annotations) = inspect.getfullargspec(fn)  # pylint: disable=deprecated-method,no-member

  except TypeError:
    # If we can't get the argspec, how do we know if the fn should take args?
    # 1. If it's a builtin, it can take args.
    # 2. If it's an implicit __init__ function (a 'slot wrapper'), take no args.
    # Are there other cases?
    if inspect.isbuiltin(fn):
      return FullArgSpec(varargs='vars', varkw='kwargs')
    return FullArgSpec()

  if skip_arg and args:
    args.pop(0)  # Remove 'self' or 'cls' from the list of arguments.

  return FullArgSpec(args, varargs, varkw, defaults,
                     kwonlyargs, kwonlydefaults, annotations)


def GetFileAndLine(component):
  """Returns the filename and line number of component.

  Args:
    component: A component to find the source information for, usually a class
        or routine.
  Returns:
    filename: The name of the file where component is defined.
    lineno: The line number where component is defined.
  """
  if inspect.isbuiltin(component):
    return None, None

  try:
    filename = inspect.getsourcefile(component)
  except TypeError:
    return None, None

  try:
    unused_code, lineindex = inspect.findsource(component)
    lineno = lineindex + 1
  except IOError:
    lineno = None

  return filename, lineno


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
  try:
    from IPython.core import oinspect  # pylint: disable=g-import-not-at-top
    inspector = oinspect.Inspector()
    info = inspector.info(component)
  except ImportError:
    info = _InfoBackup(component)

  try:
    unused_code, lineindex = inspect.findsource(component)
    info['line'] = lineindex + 1
  except (TypeError, IOError):
    info['line'] = None

  return info


def _InfoBackup(component):
  """Returns a dict with information about the given component.

  This function is to be called only in the case that IPython's
  oinspect module is not available. The info dict it produces may
  contain less information that contained in the info dict produced
  by oinspect.

  Args:
    component: The component to analyze.
  Returns:
    A dict with information about the component.
  """
  info = {}

  info['type_name'] = type(component).__name__
  info['string_form'] = str(component)

  filename, lineno = GetFileAndLine(component)
  info['file'] = filename
  info['line'] = lineno
  info['docstring'] = inspect.getdoc(component)

  try:
    info['length'] = str(len(component))
  except (TypeError, AttributeError):
    pass

  return info
