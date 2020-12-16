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

"""Python Fire is a library for creating CLIs from absolutely any Python object.

You can call Fire on any Python object:
functions, classes, modules, objects, dictionaries, lists, tuples, etc.
They all work!

Python Fire turns any Python object into a command line interface.
Simply call the Fire function as your main method to create a CLI.

When using Fire to build a CLI, your main method includes a call to Fire. Eg:

def main(argv):
  fire.Fire(Component)

A Fire CLI command is run by consuming the arguments in the command in order to
access a member of current component, call the current component (if it's a
function), or instantiate the current component (if it's a class). The target
component begins as Component, and at each operation the component becomes the
result of the preceding operation.

For example "command fn arg1 arg2" might access the "fn" property of the initial
target component, and then call that function with arguments 'arg1' and 'arg2'.
Additional examples are available in the examples directory.

Fire Flags, common to all Fire CLIs, must go after a separating "--". For
example, to get help for a command you might run: `command -- --help`.

The available flags for all Fire CLIs are:
  -v --verbose: Include private members in help and usage information.
  -h --help: Provide help and usage information for the command.
  -i --interactive: Drop into a Python REPL after running the command.
  --completion: Write the Bash completion script for the tool to stdout.
  --completion fish: Write the Fish completion script for the tool to stdout.
  --separator SEPARATOR: Use SEPARATOR in place of the default separator, '-'.
  --trace: Get the Fire Trace for the command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import json
import os
import pipes
import re
import shlex
import sys
import types

from fire import completion
from fire import decorators
from fire import formatting
from fire import helptext
from fire import inspectutils
from fire import interact
from fire import parser
from fire import trace
from fire import value_types
from fire.console import console_io
import six

if six.PY34:
  import asyncio  # pylint: disable=import-error,g-import-not-at-top  # pytype: disable=import-error


def Fire(component=None, command=None, name=None):
  """This function, Fire, is the main entrypoint for Python Fire.

  Executes a command either from the `command` argument or from sys.argv by
  recursively traversing the target object `component`'s members consuming
  arguments, evaluating functions, and instantiating classes as it goes.

  When building a CLI with Fire, your main method should call this function.

  Args:
    component: The initial target component.
    command: Optional. If supplied, this is the command executed. If not
        supplied, then the command is taken from sys.argv instead. This can be
        a string or a list of strings; a list of strings is preferred.
    name: Optional. The name of the command as entered at the command line.
        Used in interactive mode and for generating the completion script.
  Returns:
    The result of executing the Fire command. Execution begins with the initial
    target component. The component is updated by using the command arguments
    to either access a member of the current component, call the current
    component (if it's a function), or instantiate the current component (if
    it's a class). When all arguments are consumed and there's no function left
    to call or class left to instantiate, the resulting current component is
    the final result.
  Raises:
    ValueError: If the command argument is supplied, but not a string or a
        sequence of arguments.
    FireExit: When Fire encounters a FireError, Fire will raise a FireExit with
        code 2. When used with the help or trace flags, Fire will raise a
        FireExit with code 0 if successful.
  """
  name = name or os.path.basename(sys.argv[0])

  # Get args as a list.
  if isinstance(command, six.string_types):
    args = shlex.split(command)
  elif isinstance(command, (list, tuple)):
    args = command
  elif command is None:
    # Use the command line args by default if no command is specified.
    args = sys.argv[1:]
  else:
    raise ValueError('The command argument must be a string or a sequence of '
                     'arguments.')

  args, flag_args = parser.SeparateFlagArgs(args)

  argparser = parser.CreateParser()
  parsed_flag_args, unused_args = argparser.parse_known_args(flag_args)

  context = {}
  if parsed_flag_args.interactive or component is None:
    # Determine the calling context.
    caller = inspect.stack()[1]
    caller_frame = caller[0]
    caller_globals = caller_frame.f_globals
    caller_locals = caller_frame.f_locals
    context.update(caller_globals)
    context.update(caller_locals)

  component_trace = _Fire(component, args, parsed_flag_args, context, name)

  if component_trace.HasError():
    _DisplayError(component_trace)
    raise FireExit(2, component_trace)
  if component_trace.show_trace and component_trace.show_help:
    output = ['Fire trace:\n{trace}\n'.format(trace=component_trace)]
    result = component_trace.GetResult()
    help_text = helptext.HelpText(
        result, trace=component_trace, verbose=component_trace.verbose)
    output.append(help_text)
    Display(output, out=sys.stderr)
    raise FireExit(0, component_trace)
  if component_trace.show_trace:
    output = ['Fire trace:\n{trace}'.format(trace=component_trace)]
    Display(output, out=sys.stderr)
    raise FireExit(0, component_trace)
  if component_trace.show_help:
    result = component_trace.GetResult()
    help_text = helptext.HelpText(
        result, trace=component_trace, verbose=component_trace.verbose)
    output = [help_text]
    Display(output, out=sys.stderr)
    raise FireExit(0, component_trace)

  # The command succeeded normally; print the result.
  _PrintResult(component_trace, verbose=component_trace.verbose)
  result = component_trace.GetResult()
  return result


def Display(lines, out):
  text = '\n'.join(lines) + '\n'
  console_io.More(text, out=out)


def CompletionScript(name, component, shell):
  """Returns the text of the completion script for a Fire CLI."""
  return completion.Script(name, component, shell=shell)


class FireError(Exception):
  """Exception used by Fire when a Fire command cannot be executed.

  These exceptions are not raised by the Fire function, but rather are caught
  and added to the FireTrace.
  """


class FireExit(SystemExit):  # pylint: disable=g-bad-exception-name
  """An exception raised by Fire to the client in the case of a FireError.

  The trace of the Fire program is available on the `trace` property.

  This exception inherits from SystemExit, so clients may explicitly catch it
  with `except SystemExit` or `except FireExit`. If not caught, this exception
  will cause the client program to exit without a stacktrace.
  """

  def __init__(self, code, component_trace):
    """Constructs a FireExit exception.

    Args:
      code: (int) Exit code for the Fire CLI.
      component_trace: (FireTrace) The trace for the Fire command.
    """
    super(FireExit, self).__init__(code)
    self.trace = component_trace


def _IsHelpShortcut(component_trace, remaining_args):
  """Determines if the user is trying to access help without '--' separator.

  For example, mycmd.py --help instead of mycmd.py -- --help.

  Args:
    component_trace: (FireTrace) The trace for the Fire command.
    remaining_args: List of remaining args that haven't been consumed yet.
  Returns:
    True if help is requested, False otherwise.
  """
  show_help = False
  if remaining_args:
    target = remaining_args[0]
    if target in ('-h', '--help'):
      # Check if --help would be consumed as a keyword argument, or is a member.
      component = component_trace.GetResult()
      if inspect.isclass(component) or inspect.isroutine(component):
        fn_spec = inspectutils.GetFullArgSpec(component)
        _, remaining_kwargs, _ = _ParseKeywordArgs(remaining_args, fn_spec)
        show_help = target in remaining_kwargs
      else:
        members = dict(inspect.getmembers(component))
        show_help = target not in members

  if show_help:
    component_trace.show_help = True
    command = '{cmd} -- --help'.format(cmd=component_trace.GetCommand())
    print('INFO: Showing help with the command {cmd}.\n'.format(
        cmd=pipes.quote(command)), file=sys.stderr)
  return show_help


def _PrintResult(component_trace, verbose=False):
  """Prints the result of the Fire call to stdout in a human readable way."""
  # TODO(dbieber): Design human readable deserializable serialization method
  # and move serialization to its own module.
  result = component_trace.GetResult()

  if value_types.HasCustomStr(result):
    # If the object has a custom __str__ method, rather than one inherited from
    # object, then we use that to serialize the object.
    print(str(result))
    return

  if isinstance(result, (list, set, frozenset, types.GeneratorType)):
    for i in result:
      print(_OneLineResult(i))
  elif inspect.isgeneratorfunction(result):
    raise NotImplementedError
  elif isinstance(result, dict) and value_types.IsSimpleGroup(result):
    print(_DictAsString(result, verbose))
  elif isinstance(result, tuple):
    print(_OneLineResult(result))
  elif isinstance(result, value_types.VALUE_TYPES):
    if result is not None:
      print(result)
  else:
    help_text = helptext.HelpText(
        result, trace=component_trace, verbose=verbose)
    output = [help_text]
    Display(output, out=sys.stdout)


def _DisplayError(component_trace):
  """Prints the Fire trace and the error to stdout."""
  result = component_trace.GetResult()

  output = []
  show_help = False
  for help_flag in ('-h', '--help'):
    if help_flag in component_trace.elements[-1].args:
      show_help = True

  if show_help:
    command = '{cmd} -- --help'.format(cmd=component_trace.GetCommand())
    print('INFO: Showing help with the command {cmd}.\n'.format(
        cmd=pipes.quote(command)), file=sys.stderr)
    help_text = helptext.HelpText(result, trace=component_trace,
                                  verbose=component_trace.verbose)
    output.append(help_text)
    Display(output, out=sys.stderr)
  else:
    print(formatting.Error('ERROR: ')
          + component_trace.elements[-1].ErrorAsStr(),
          file=sys.stderr)
    error_text = helptext.UsageText(result, trace=component_trace,
                                    verbose=component_trace.verbose)
    print(error_text, file=sys.stderr)


def _DictAsString(result, verbose=False):
  """Returns a dict as a string.

  Args:
    result: The dict to convert to a string
    verbose: Whether to include 'hidden' members, those keys starting with _.
  Returns:
    A string representing the dict
  """

  # We need to do 2 iterations over the items in the result dict
  # 1) Getting visible items and the longest key for output formatting
  # 2) Actually construct the output lines
  class_attrs = inspectutils.GetClassAttrsDict(result)
  result_visible = {
      key: value for key, value in result.items()
      if completion.MemberVisible(result, key, value,
                                  class_attrs=class_attrs, verbose=verbose)
  }

  if not result_visible:
    return '{}'

  longest_key = max(len(str(key)) for key in result_visible.keys())
  format_string = '{{key:{padding}s}} {{value}}'.format(padding=longest_key + 1)

  lines = []
  for key, value in result.items():
    if completion.MemberVisible(result, key, value, class_attrs=class_attrs,
                                verbose=verbose):
      line = format_string.format(key=str(key) + ':',
                                  value=_OneLineResult(value))
      lines.append(line)
  return '\n'.join(lines)


def _OneLineResult(result):
  """Returns result serialized to a single line string."""
  # TODO(dbieber): Ensure line is fewer than eg 120 characters.
  if isinstance(result, six.string_types):
    return str(result).replace('\n', ' ')

  # TODO(dbieber): Show a small amount of usage information about the function
  # or module if it fits cleanly on the line.
  if inspect.isfunction(result):
    return '<function {name}>'.format(name=result.__name__)

  if inspect.ismodule(result):
    return '<module {name}>'.format(name=result.__name__)

  try:
    # Don't force conversion to ascii.
    return json.dumps(result, ensure_ascii=False)
  except (TypeError, ValueError):
    return str(result).replace('\n', ' ')


def _Fire(component, args, parsed_flag_args, context, name=None):
  """Execute a Fire command on a target component using the args supplied.

  Arguments that come after a final isolated '--' are treated as Flags, eg for
  interactive mode or completion script generation.

  Other arguments are consumed by the execution of the Fire command, eg in the
  traversal of the members of the component, or in calling a function or
  instantiating a class found during the traversal.

  The steps performed by this method are:

  1. Parse any Flag args (the args after the final --)

  2. Start with component as the current component.
  2a. If the current component is a class, instantiate it using args from args.
  2b. If the component is a routine, call it using args from args.
  2c. If the component is a sequence, index into it using an arg from
      args.
  2d. If possible, access a member from the component using an arg from args.
  2e. If the component is a callable object, call it using args from args.
  2f. Repeat 2a-2e until no args remain.
  Note: Only the first applicable rule from 2a-2e is applied in each iteration.
  After each iteration of step 2a-2e, the current component is updated to be the
  result of the applied rule.

  3a. Embed into ipython REPL if interactive mode is selected.
  3b. Generate a completion script if that flag is provided.

  In step 2, arguments will only ever be consumed up to a separator; a single
  step will never consume arguments from both sides of a separator.
  The separator defaults to a hyphen (-), and can be overwritten with the
  --separator Fire argument.

  Args:
    component: The target component for Fire.
    args: A list of args to consume in Firing on the component, usually from
        the command line.
    parsed_flag_args: The values of the flag args (e.g. --verbose, --separator)
        that are part of every Fire CLI.
    context: A dict with the local and global variables available at the call
        to Fire.
    name: Optional. The name of the command. Used in interactive mode and in
        the tab completion script.
  Returns:
    FireTrace of components starting with component, tracing Fire's execution
        path as it consumes args.
  Raises:
    ValueError: If there are arguments that cannot be consumed.
    ValueError: If --completion is specified but no name available.
  """
  verbose = parsed_flag_args.verbose
  interactive = parsed_flag_args.interactive
  separator = parsed_flag_args.separator
  show_completion = parsed_flag_args.completion
  show_help = parsed_flag_args.help
  show_trace = parsed_flag_args.trace

  # component can be a module, class, routine, object, etc.
  if component is None:
    component = context

  initial_component = component
  component_trace = trace.FireTrace(
      initial_component=initial_component, name=name, separator=separator,
      verbose=verbose, show_help=show_help, show_trace=show_trace)

  instance = None
  remaining_args = args
  while True:
    last_component = component
    initial_args = remaining_args

    if not remaining_args and (show_help or interactive or show_trace
                               or show_completion is not None):
      # Don't initialize the final class or call the final function unless
      # there's a separator after it, and instead process the current component.
      break

    if _IsHelpShortcut(component_trace, remaining_args):
      remaining_args = []
      break

    saved_args = []
    used_separator = False
    if separator in remaining_args:
      # For the current component, only use arguments up to the separator.
      separator_index = remaining_args.index(separator)
      saved_args = remaining_args[separator_index + 1:]
      remaining_args = remaining_args[:separator_index]
      used_separator = True
    assert separator not in remaining_args

    handled = False
    candidate_errors = []

    is_callable = inspect.isclass(component) or inspect.isroutine(component)
    is_callable_object = callable(component) and not is_callable
    is_sequence = isinstance(component, (list, tuple))
    is_map = isinstance(component, dict) or inspectutils.IsNamedTuple(component)

    if not handled and is_callable:
      # The component is a class or a routine; we'll try to initialize it or
      # call it.
      is_class = inspect.isclass(component)

      try:
        component, remaining_args = _CallAndUpdateTrace(
            component,
            remaining_args,
            component_trace,
            treatment='class' if is_class else 'routine',
            target=component.__name__)
        handled = True
      except FireError as error:
        candidate_errors.append((error, initial_args))

      if handled and last_component is initial_component:
        # If the initial component is a class, keep an instance for use with -i.
        instance = component

    if not handled and is_sequence and remaining_args:
      # The component is a tuple or list; we'll try to access a member.
      arg = remaining_args[0]
      try:
        index = int(arg)
        component = component[index]
        handled = True
      except (ValueError, IndexError):
        error = FireError(
            'Unable to index into component with argument:', arg)
        candidate_errors.append((error, initial_args))

      if handled:
        remaining_args = remaining_args[1:]
        filename = None
        lineno = None
        component_trace.AddAccessedProperty(
            component, index, [arg], filename, lineno)

    if not handled and is_map and remaining_args:
      # The component is a dict or other key-value map; try to access a member.
      target = remaining_args[0]

      # Treat namedtuples as dicts when handling them as a map.
      if inspectutils.IsNamedTuple(component):
        component_dict = component._asdict()  # pytype: disable=attribute-error
      else:
        component_dict = component

      if target in component_dict:
        component = component_dict[target]
        handled = True
      elif target.replace('-', '_') in component_dict:
        component = component_dict[target.replace('-', '_')]
        handled = True
      else:
        # The target isn't present in the dict as a string key, but maybe it is
        # a key as another type.
        # TODO(dbieber): Consider alternatives for accessing non-string keys.
        for key, value in component_dict.items():
          if target == str(key):
            component = value
            handled = True
            break

      if handled:
        remaining_args = remaining_args[1:]
        filename = None
        lineno = None
        component_trace.AddAccessedProperty(
            component, target, [target], filename, lineno)
      else:
        error = FireError('Cannot find key:', target)
        candidate_errors.append((error, initial_args))

    if not handled and remaining_args:
      # Object handler. We'll try to access a member of the component.
      try:
        target = remaining_args[0]

        component, consumed_args, remaining_args = _GetMember(
            component, remaining_args)
        handled = True

        filename, lineno = inspectutils.GetFileAndLine(component)

        component_trace.AddAccessedProperty(
            component, target, consumed_args, filename, lineno)

      except FireError as error:
        # Couldn't access member.
        candidate_errors.append((error, initial_args))

    if not handled and is_callable_object:
      # The component is a callable object; we'll try to call it.
      try:
        component, remaining_args = _CallAndUpdateTrace(
            component,
            remaining_args,
            component_trace,
            treatment='callable')
        handled = True
      except FireError as error:
        candidate_errors.append((error, initial_args))

    if not handled and candidate_errors:
      error, initial_args = candidate_errors[0]
      component_trace.AddError(error, initial_args)
      return component_trace

    if used_separator:
      # Add back in the arguments from after the separator.
      if remaining_args:
        remaining_args = remaining_args + [separator] + saved_args
      elif (inspect.isclass(last_component)
            or inspect.isroutine(last_component)):
        remaining_args = saved_args
        component_trace.AddSeparator()
      elif component is not last_component:
        remaining_args = [separator] + saved_args
      else:
        # It was an unnecessary separator.
        remaining_args = saved_args

    if component is last_component and remaining_args == initial_args:
      # We're making no progress.
      break

  if remaining_args:
    component_trace.AddError(
        FireError('Could not consume arguments:', remaining_args),
        initial_args)
    return component_trace

  if show_completion is not None:
    if name is None:
      raise ValueError('Cannot make completion script without command name')
    script = CompletionScript(name, initial_component, shell=show_completion)
    component_trace.AddCompletionScript(script)

  if interactive:
    variables = context.copy()

    if name is not None:
      variables[name] = initial_component
    variables['component'] = initial_component
    variables['result'] = component
    variables['trace'] = component_trace

    if instance is not None:
      variables['self'] = instance

    interact.Embed(variables, verbose)

    component_trace.AddInteractiveMode()

  return component_trace


def _GetMember(component, args):
  """Returns a subcomponent of component by consuming an arg from args.

  Given a starting component and args, this function gets a member from that
  component, consuming one arg in the process.

  Args:
    component: The component from which to get a member.
    args: Args from which to consume in the search for the next component.
  Returns:
    component: The component that was found by consuming an arg.
    consumed_args: The args that were consumed by getting this member.
    remaining_args: The remaining args that haven't been consumed yet.
  Raises:
    FireError: If we cannot consume an argument to get a member.
  """
  members = dir(component)
  arg = args[0]
  arg_names = [
      arg,
      arg.replace('-', '_'),  # treat '-' as '_'.
  ]

  for arg_name in arg_names:
    if arg_name in members:
      return getattr(component, arg_name), [arg], args[1:]

  raise FireError('Could not consume arg:', arg)


def _CallAndUpdateTrace(component, args, component_trace, treatment='class',
                        target=None):
  """Call the component by consuming args from args, and update the FireTrace.

  The component could be a class, a routine, or a callable object. This function
  calls the component and adds the appropriate action to component_trace.

  Args:
    component: The component to call
    args: Args for calling the component
    component_trace: FireTrace object that contains action trace
    treatment: Type of treatment used. Indicating whether we treat the component
        as a class, a routine, or a callable.
    target: Target in FireTrace element, default is None. If the value is None,
        the component itself will be used as target.
  Returns:
    component: The object that is the result of the callable call.
    remaining_args: The remaining args that haven't been consumed yet.
  """
  if not target:
    target = component
  filename, lineno = inspectutils.GetFileAndLine(component)
  metadata = decorators.GetMetadata(component)
  fn = component.__call__ if treatment == 'callable' else component
  parse = _MakeParseFn(fn, metadata)
  (varargs, kwargs), consumed_args, remaining_args, capacity = parse(args)

  # Call the function.
  if inspectutils.IsCoroutineFunction(fn):
    loop = asyncio.get_event_loop()
    component = loop.run_until_complete(fn(*varargs, **kwargs))
  else:
    component = fn(*varargs, **kwargs)

  if treatment == 'class':
    action = trace.INSTANTIATED_CLASS
  elif treatment == 'routine':
    action = trace.CALLED_ROUTINE
  else:
    action = trace.CALLED_CALLABLE
  component_trace.AddCalledComponent(
      component, target, consumed_args, filename, lineno, capacity,
      action=action)

  return component, remaining_args


def _MakeParseFn(fn, metadata):
  """Creates a parse function for fn.

  Args:
    fn: The function or class to create the parse function for.
    metadata: Additional metadata about the component the parse function is for.
  Returns:
    A parse function for fn. The parse function accepts a list of arguments
    and returns (varargs, kwargs), remaining_args. The original function fn
    can then be called with fn(*varargs, **kwargs). The remaining_args are
    the leftover args from the arguments to the parse function.
  """
  fn_spec = inspectutils.GetFullArgSpec(fn)

  # Note: num_required_args is the number of positional arguments without
  # default values. All of these arguments are required.
  num_required_args = len(fn_spec.args) - len(fn_spec.defaults)
  required_kwonly = set(fn_spec.kwonlyargs) - set(fn_spec.kwonlydefaults)

  def _ParseFn(args):
    """Parses the list of `args` into (varargs, kwargs), remaining_args."""
    kwargs, remaining_kwargs, remaining_args = _ParseKeywordArgs(args, fn_spec)

    # Note: _ParseArgs modifies kwargs.
    parsed_args, kwargs, remaining_args, capacity = _ParseArgs(
        fn_spec.args, fn_spec.defaults, num_required_args, kwargs,
        remaining_args, metadata)

    if fn_spec.varargs or fn_spec.varkw:
      # If we're allowed *varargs or **kwargs, there's always capacity.
      capacity = True

    extra_kw = set(kwargs) - set(fn_spec.kwonlyargs)
    if fn_spec.varkw is None and extra_kw:
      raise FireError('Unexpected kwargs present:', extra_kw)

    missing_kwonly = set(required_kwonly) - set(kwargs)
    if missing_kwonly:
      raise FireError('Missing required flags:', missing_kwonly)

    # If we accept *varargs, then use all remaining arguments for *varargs.
    if fn_spec.varargs is not None:
      varargs, remaining_args = remaining_args, []
    else:
      varargs = []

    for index, value in enumerate(varargs):
      varargs[index] = _ParseValue(value, None, None, metadata)

    varargs = parsed_args + varargs
    remaining_args += remaining_kwargs

    consumed_args = args[:len(args) - len(remaining_args)]
    return (varargs, kwargs), consumed_args, remaining_args, capacity

  return _ParseFn


def _ParseArgs(fn_args, fn_defaults, num_required_args, kwargs,
               remaining_args, metadata):
  """Parses the positional and named arguments from the available supplied args.

  Modifies kwargs, removing args as they are used.

  Args:
    fn_args: A list of argument names that the target function accepts,
        including positional and named arguments, but not the varargs or kwargs
        names.
    fn_defaults: A list of the default values in the function argspec.
    num_required_args: The number of required arguments from the function's
        argspec. This is the number of arguments without a default value.
    kwargs: Dict with named command line arguments and their values.
    remaining_args: The remaining command line arguments, which may still be
        used as positional arguments.
    metadata: Metadata about the function, typically from Fire decorators.
  Returns:
    parsed_args: A list of values to be used as positional arguments for calling
        the target function.
    kwargs: The input dict kwargs modified with the used kwargs removed.
    remaining_args: A list of the supplied args that have not been used yet.
    capacity: Whether the call could have taken args in place of defaults.
  Raises:
    FireError: If additional positional arguments are expected, but none are
        available.
  """
  accepts_positional_args = metadata.get(decorators.ACCEPTS_POSITIONAL_ARGS)
  capacity = False  # If we see a default get used, we'll set capacity to True

  # Select unnamed args.
  parsed_args = []
  for index, arg in enumerate(fn_args):
    value = kwargs.pop(arg, None)
    if value is not None:  # A value is specified at the command line.
      value = _ParseValue(value, index, arg, metadata)
      parsed_args.append(value)
    else:  # No value has been explicitly specified.
      if remaining_args and accepts_positional_args:
        # Use a positional arg.
        value = remaining_args.pop(0)
        value = _ParseValue(value, index, arg, metadata)
        parsed_args.append(value)
      elif index < num_required_args:
        raise FireError(
            'The function received no value for the required argument:', arg)
      else:
        # We're past the args for which there's no default value.
        # There's a default value for this arg.
        capacity = True
        default_index = index - num_required_args  # index into the defaults.
        parsed_args.append(fn_defaults[default_index])

  for key, value in kwargs.items():
    kwargs[key] = _ParseValue(value, None, key, metadata)

  return parsed_args, kwargs, remaining_args, capacity


def _ParseKeywordArgs(args, fn_spec):
  """Parses the supplied arguments for keyword arguments.

  Given a list of arguments, finds occurrences of --name value, and uses 'name'
  as the keyword and 'value' as the value. Constructs and returns a dictionary
  of these keyword arguments, and returns a list of the remaining arguments.

  Only if fn_keywords is None, this only finds argument names used by the
  function, specified through fn_args.

  This returns the values of the args as strings. They are later processed by
  _ParseArgs, which converts them to the appropriate type.

  Args:
    args: A list of arguments.
    fn_spec: The inspectutils.FullArgSpec describing the given callable.
  Returns:
    kwargs: A dictionary mapping keywords to values.
    remaining_kwargs: A list of the unused kwargs from the original args.
    remaining_args: A list of the unused arguments from the original args.
  Raises:
    FireError: If a single-character flag is passed that could refer to multiple
        possible args.
  """
  kwargs = {}
  remaining_kwargs = []
  remaining_args = []
  fn_keywords = fn_spec.varkw
  fn_args = fn_spec.args + fn_spec.kwonlyargs

  if not args:
    return kwargs, remaining_kwargs, remaining_args

  skip_argument = False

  for index, argument in enumerate(args):
    if skip_argument:
      skip_argument = False
      continue

    if _IsFlag(argument):
      # This is a named argument. We get its value from this arg or the next.

      # Terminology:
      # argument: A full token from the command line, e.g. '--alpha=10'
      # stripped_argument: An argument without leading hyphens.
      # key: The contents of the stripped argument up to the first equal sign.
      # "shortcut flag": refers to an argument where the key is just the first
      #   letter of a longer keyword.
      # keyword: The Python function argument being set by this argument.
      # value: The unparsed value for that Python function argument.
      contains_equals = '=' in argument
      stripped_argument = argument.lstrip('-')
      if contains_equals:
        key, value = stripped_argument.split('=', 1)
      else:
        key = stripped_argument

      key = key.replace('-', '_')
      is_bool_syntax = (not contains_equals and
                        (index + 1 == len(args) or _IsFlag(args[index + 1])))

      # Determine the keyword.
      keyword = ''  # Indicates no valid keyword has been found yet.
      if (key in fn_args
          or (is_bool_syntax and key.startswith('no') and key[2:] in fn_args)
          or fn_keywords):
        keyword = key
      elif len(key) == 1:
        # This may be a shortcut flag.
        matching_fn_args = [arg for arg in fn_args if arg[0] == key]
        if len(matching_fn_args) == 1:
          keyword = matching_fn_args[0]
        elif len(matching_fn_args) > 1:
          raise FireError("The argument '{}' is ambiguous as it could "
                          "refer to any of the following arguments: {}".format(
                              argument, matching_fn_args))

      # Determine the value.
      if not keyword:
        got_argument = False
      elif contains_equals:
        # Already got the value above.
        got_argument = True
      elif is_bool_syntax:
        # There's no next arg or the next arg is a Flag, so we consider this
        # flag to be a boolean.
        got_argument = True
        if keyword in fn_args:
          value = 'True'
        elif keyword.startswith('no'):
          keyword = keyword[2:]
          value = 'False'
        else:
          value = 'True'
      else:
        # The assert should pass. Otherwise either contains_equals or
        # is_bool_syntax would have been True.
        assert index + 1 < len(args)
        value = args[index + 1]
        got_argument = True

      # In order for us to consume the argument as a keyword arg, we either:
      # Need to be explicitly expecting the keyword, or we need to be
      # accepting **kwargs.
      skip_argument = not contains_equals and not is_bool_syntax
      if got_argument:
        kwargs[keyword] = value
      else:
        remaining_kwargs.append(argument)
        if skip_argument:
          remaining_kwargs.append(args[index + 1])
    else:  # not _IsFlag(argument)
      remaining_args.append(argument)

  return kwargs, remaining_kwargs, remaining_args


def _IsFlag(argument):
  """Determines if the argument is a flag argument.

  If it starts with a hyphen and isn't a negative number, it's a flag.

  Args:
    argument: A command line argument that may or may not be a flag.
  Returns:
    A boolean indicating whether the argument is a flag.
  """
  return _IsSingleCharFlag(argument) or _IsMultiCharFlag(argument)


def _IsSingleCharFlag(argument):
  """Determines if the argument is a single char flag (e.g. '-a')."""
  return re.match('^-[a-zA-Z]$', argument) or re.match('^-[a-zA-Z]=', argument)


def _IsMultiCharFlag(argument):
  """Determines if the argument is a multi char flag (e.g. '--alpha')."""
  return argument.startswith('--') or re.match('^-[a-zA-Z]', argument)


def _ParseValue(value, index, arg, metadata):
  """Parses value, a string, into the appropriate type.

  The function used to parse value is determined by the remaining arguments.

  Args:
    value: The string value to be parsed, typically a command line argument.
    index: The index of the value in the function's argspec.
    arg: The name of the argument the value is being parsed for.
    metadata: Metadata about the function, typically from Fire decorators.
  Returns:
    value, parsed into the appropriate type for calling a function.
  """
  parse_fn = parser.DefaultParseValue

  # We check to see if any parse function from the fn metadata applies here.
  parse_fns = metadata.get(decorators.FIRE_PARSE_FNS)
  if parse_fns:
    default = parse_fns['default']
    positional = parse_fns['positional']
    named = parse_fns['named']

    if index is not None and 0 <= index < len(positional):
      parse_fn = positional[index]
    elif arg in named:
      parse_fn = named[arg]
    elif default is not None:
      parse_fn = default

  return parse_fn(value)
