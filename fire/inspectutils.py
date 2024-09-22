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

"""Inspection utility functions for Python Fire."""

import asyncio
import inspect
import sys
import types

from fire import docstrings


class FullArgSpec:
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
      fn: The function to use for determining the arg spec of this function.
      skip_arg: Whether the first argument will be supplied automatically, and
        hence should be skipped when supplying args from a Fire command.
  """
  skip_arg = False
  if inspect.isclass(fn):
    # If the function is a class, we try to use its init method.
    skip_arg = True
  elif inspect.ismethod(fn):
    # If the function is a bound method, we skip the `self` argument.
    skip_arg = fn.__self__ is not None
  elif inspect.isbuiltin(fn):
    # If the function is a bound builtin, we skip the `self` argument, unless
    # the function is from a standard library module in which case its __self__
    # attribute is that module.
    if not isinstance(fn.__self__, types.ModuleType):
      skip_arg = True
  elif not inspect.isfunction(fn):
    # The purpose of this else clause is to set skip_arg for callable objects.
    skip_arg = True
  return fn, skip_arg


def Py3GetFullArgSpec(fn):
  """A alternative to the builtin getfullargspec.

  The builtin inspect.getfullargspec uses:
  `skip_bound_args=False, follow_wrapped_chains=False`
  in order to be backwards compatible.

  This function instead skips bound args (self) and follows wrapped chains.

  Args:
    fn: The function or class of interest.
  Returns:
    An inspect.FullArgSpec namedtuple with the full arg spec of the function.
  """
  # pylint: disable=no-member
  # pytype: disable=module-attr
  try:
    sig = inspect._signature_from_callable(  # pylint: disable=protected-access
        fn,
        skip_bound_arg=True,
        follow_wrapper_chains=True,
        sigcls=inspect.Signature)
  except Exception:
    # 'signature' can raise ValueError (most common), AttributeError, and
    # possibly others. We catch all exceptions here, and reraise a TypeError.
    raise TypeError('Unsupported callable.')

  args = []
  varargs = None
  varkw = None
  kwonlyargs = []
  defaults = ()
  annotations = {}
  defaults = ()
  kwdefaults = {}

  if sig.return_annotation is not sig.empty:
    annotations['return'] = sig.return_annotation

  for param in sig.parameters.values():
    kind = param.kind
    name = param.name

    # pylint: disable=protected-access
    if kind is inspect._POSITIONAL_ONLY:
      args.append(name)
    elif kind is  inspect._POSITIONAL_OR_KEYWORD:
      args.append(name)
      if param.default is not param.empty:
        defaults += (param.default,)
    elif kind is  inspect._VAR_POSITIONAL:
      varargs = name
    elif kind is  inspect._KEYWORD_ONLY:
      kwonlyargs.append(name)
      if param.default is not param.empty:
        kwdefaults[name] = param.default
    elif kind is  inspect._VAR_KEYWORD:
      varkw = name
    if param.annotation is not param.empty:
      annotations[name] = param.annotation
    # pylint: enable=protected-access

  if not kwdefaults:
    # compatibility with 'func.__kwdefaults__'
    kwdefaults = None

  if not defaults:
    # compatibility with 'func.__defaults__'
    defaults = None
  return inspect.FullArgSpec(args, varargs, varkw, defaults,
                             kwonlyargs, kwdefaults, annotations)
  # pylint: enable=no-member
  # pytype: enable=module-attr


def GetFullArgSpec(fn):
  """Returns a FullArgSpec describing the given callable."""
  original_fn = fn
  fn, skip_arg = _GetArgSpecInfo(fn)

  try:
    if sys.version_info[0:2] >= (3, 5):
      (args, varargs, varkw, defaults,
       kwonlyargs, kwonlydefaults, annotations) = Py3GetFullArgSpec(fn)
    else:  # Specifically Python 3.4.
      (args, varargs, varkw, defaults,
       kwonlyargs, kwonlydefaults, annotations) = inspect.getfullargspec(fn)  # pylint: disable=deprecated-method,no-member

  except TypeError:
    # If we can't get the argspec, how do we know if the fn should take args?
    # 1. If it's a builtin, it can take args.
    # 2. If it's an implicit __init__ function (a 'slot wrapper'), that comes
    # from a namedtuple, use _fields to determine the args.
    # 3. If it's another slot wrapper (that comes from not subclassing object in
    # Python 2), then there are no args.
    # Are there other cases? We just don't know.

    # Case 1: Builtins accept args.
    if inspect.isbuiltin(fn):
      # TODO(dbieber): Try parsing the docstring, if available.
      # TODO(dbieber): Use known argspecs, like set.add and namedtuple.count.
      return FullArgSpec(varargs='vars', varkw='kwargs')

    # Case 2: namedtuples store their args in their _fields attribute.
    # TODO(dbieber): Determine if there's a way to detect false positives.
    # In Python 2, a class that does not subclass anything, does not define
    # __init__, and has an attribute named _fields will cause Fire to think it
    # expects args for its constructor when in fact it does not.
    fields = getattr(original_fn, '_fields', None)
    if fields is not None:
      return FullArgSpec(args=list(fields))

    # Case 3: Other known slot wrappers do not accept args.
    return FullArgSpec()

  # In Python 3.5+ Py3GetFullArgSpec uses skip_bound_arg=True already.
  skip_arg_required = sys.version_info[0:2] == (3, 4)
  if skip_arg_required and skip_arg and args:
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
  except (OSError, IndexError):
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
    from IPython.core import oinspect  # pylint: disable=import-outside-toplevel,g-import-not-at-top
    inspector = oinspect.Inspector()
    info = inspector.info(component)

    # IPython's oinspect.Inspector.info may return '<no docstring>'
    if info['docstring'] == '<no docstring>':
      info['docstring'] = None
  except ImportError:
    info = _InfoBackup(component)

  try:
    unused_code, lineindex = inspect.findsource(component)
    info['line'] = lineindex + 1
  except (TypeError, OSError):
    info['line'] = None

  if 'docstring' in info:
    info['docstring_info'] = docstrings.parse(info['docstring'])

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


def IsNamedTuple(component):
  """Return true if the component is a namedtuple.

  Unfortunately, Python offers no native way to check for a namedtuple type.
  Instead, we need to use a simple hack which should suffice for our case.
  namedtuples are internally implemented as tuples, therefore we need to:
    1. Check if the component is an instance of tuple.
    2. Check if the component has a _fields attribute which regular tuples do
       not have.

  Args:
    component: The component to analyze.
  Returns:
    True if the component is a namedtuple or False otherwise.
  """
  if not isinstance(component, tuple):
    return False

  has_fields = bool(getattr(component, '_fields', None))
  return has_fields


def GetClassAttrsDict(component):
  """Gets the attributes of the component class, as a dict with name keys."""
  if not inspect.isclass(component):
    return None
  class_attrs_list = inspect.classify_class_attrs(component)
  return {
      class_attr.name: class_attr
      for class_attr in class_attrs_list
  }


def IsCoroutineFunction(fn):
  try:
    return asyncio.iscoroutinefunction(fn)
  except:  # pylint: disable=bare-except
    return False
