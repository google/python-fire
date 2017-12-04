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
import shlex
import sys
import types

from fire import completion
from fire import decorators
from fire import helputils
from fire import inspectutils
from fire import interact
from fire import parser
from fire import trace
import six


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

  # Determine the calling context.
  caller = inspect.stack()[1]
  caller_frame = caller[0]
  caller_globals = caller_frame.f_globals
  caller_locals = caller_frame.f_locals
  context = {}
  context.update(caller_globals)
  context.update(caller_locals)

  component_trace = _Fire(component, args, context, name)

  if component_trace.HasError():
    for help_flag in ['-h', '--help']:
      if help_flag in component_trace.elements[-1].args:
        command = '{cmd} -- --help'.format(cmd=component_trace.GetCommand())
        print(('WARNING: The proper way to show help is {cmd}.\n'
               'Showing help anyway.\n').format(cmd=pipes.quote(command)),
              file=sys.stderr)

    print('Fire trace:\n{trace}\n'.format(trace=component_trace),
          file=sys.stderr)
    result = component_trace.GetResult()
    print(
        helputils.HelpString(result, component_trace, component_trace.verbose),
        file=sys.stderr)
    raise FireExit(2, component_trace)
  elif component_trace.show_trace and component_trace.show_help:
    print('Fire trace:\n{trace}\n'.format(trace=component_trace),
          file=sys.stderr)
    result = component_trace.GetResult()
    print(
        helputils.HelpString(result, component_trace, component_trace.verbose),
        file=sys.stderr)
    raise FireExit(0, component_trace)
  elif component_trace.show_trace:
    print('Fire trace:\n{trace}'.format(trace=component_trace),
          file=sys.stderr)
    raise FireExit(0, component_trace)
  elif component_trace.show_help:
    result = component_trace.GetResult()
    print(
        helputils.HelpString(result, component_trace, component_trace.verbose),
        file=sys.stderr)
    raise FireExit(0, component_trace)
  else:
    _PrintResult(component_trace, verbose=component_trace.verbose)
    result = component_trace.GetResult()
    return result


def CompletionScript(name, component):
  """Returns the text of the Bash completion script for a Fire CLI."""
  return completion.Script(name, component)


class FireError(Exception):
  """Exception used by Fire when a Fire command cannot be executed.

  These exceptions are not raised by the Fire function, but rather are caught
  and added to the FireTrace.
  """


class FireExit(SystemExit):
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


def _PrintResult(component_trace, verbose=False):
  """Prints the result of the Fire call to stdout in a human readable way."""
  # TODO: Design human readable deserializable serialization method
  # and move serialization to it's own module.
  result = component_trace.GetResult()

  if isinstance(result, (list, set, types.GeneratorType)):
    for i in result:
      print(_OneLineResult(i))
  elif inspect.isgeneratorfunction(result):
    raise NotImplementedError
  elif isinstance(result, dict):
    print(_DictAsString(result, verbose))
  elif isinstance(result, tuple):
    print(_OneLineResult(result))
  elif isinstance(result,
                  (bool, six.string_types, six.integer_types, float, complex)):
    print(result)
  elif result is not None:
    print(helputils.HelpString(result, component_trace, verbose))


def _DictAsString(result, verbose=False):
  """Returns a dict as a string.

  Args:
    result: The dict to convert to a string
    verbose: Whether to include 'hidden' members, those keys starting with _.
  Returns:
    A string representing the dict
  """
  result = {key: value for key, value in result.items()
            if _ComponentVisible(key, verbose)}

  if not result:
    return '{}'

  longest_key = max(len(str(key)) for key in result.keys())
  format_string = '{{key:{padding}s}} {{value}}'.format(padding=longest_key + 1)

  lines = []
  for key, value in result.items():
    line = format_string.format(key=str(key) + ':',
                                value=_OneLineResult(value))
    lines.append(line)
  return '\n'.join(lines)


def _ComponentVisible(component, verbose=False):
  """Returns whether a component should be visible in the output."""
  return (
      verbose
      or not isinstance(component, six.string_types)
      or not component.startswith('_'))


def _OneLineResult(result):
  """Returns result serialized to a single line string."""
  # TODO: Ensure line is fewer than eg 120 characters.
  if isinstance(result, six.string_types):
    return str(result).replace('\n', ' ')

  try:
    # Don't force conversion to ascii.
    return json.dumps(result, ensure_ascii=False)
  except (TypeError, ValueError):
    return str(result).replace('\n', ' ')


def _Fire(component, args, context, name=None):
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
  2b. If the current component is a routine, call it using args from args.
  2c. Otherwise access a member from component using an arg from args.
  2d. Repeat 2a-2c until no args remain.

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
  args, flag_args = parser.SeparateFlagArgs(args)

  argparser = parser.CreateParser()
  parsed_flag_args, unused_args = argparser.parse_known_args(flag_args)
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
                               or show_completion):
      # Don't initialize the final class or call the final function unless
      # there's a separator after it, and instead process the current component.
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

    if inspect.isclass(component) or inspect.isroutine(component):
      # The component is a class or a routine; we'll try to initialize it or
      # call it.
      isclass = inspect.isclass(component)

      try:
        target = component.__name__
        filename, lineno = inspectutils.GetFileAndLine(component)

        component, consumed_args, remaining_args, capacity = _CallCallable(
            component, remaining_args)

        # Update the trace.
        if isclass:
          component_trace.AddInstantiatedClass(
              component, target, consumed_args, filename, lineno, capacity)
        else:
          component_trace.AddCalledRoutine(
              component, target, consumed_args, filename, lineno, capacity)

      except FireError as error:
        component_trace.AddError(error, initial_args)
        return component_trace

      if last_component is initial_component:
        # If the initial component is a class, keep an instance for use with -i.
        instance = component

    elif isinstance(component, (list, tuple)) and remaining_args:
      # The component is a tuple or list; we'll try to access a member.
      arg = remaining_args[0]
      try:
        index = int(arg)
        component = component[index]
      except (ValueError, IndexError):
        error = FireError(
            'Unable to index into component with argument:', arg)
        component_trace.AddError(error, initial_args)
        return component_trace

      remaining_args = remaining_args[1:]
      filename = None
      lineno = None
      component_trace.AddAccessedProperty(
          component, index, [arg], filename, lineno)

    elif isinstance(component, dict) and remaining_args:
      # The component is a dict; we'll try to access a member.
      target = remaining_args[0]
      if target in component:
        component = component[target]
      elif target.replace('-', '_') in component:
        component = component[target.replace('-', '_')]
      else:
        # The target isn't present in the dict as a string, but maybe it is as
        # another type.
        # TODO: Consider alternatives for accessing non-string keys.
        found_target = False
        for key, value in component.items():
          if target == str(key):
            component = value
            found_target = True
            break
        if not found_target:
          error = FireError(
              'Cannot find target in dict:', target, component)
          component_trace.AddError(error, initial_args)
          return component_trace

      remaining_args = remaining_args[1:]
      filename = None
      lineno = None
      component_trace.AddAccessedProperty(
          component, target, [target], filename, lineno)

    elif remaining_args:
      # We'll try to access a member of the component.
      try:
        target = remaining_args[0]

        component, consumed_args, remaining_args = _GetMember(
            component, remaining_args)

        filename, lineno = inspectutils.GetFileAndLine(component)

        component_trace.AddAccessedProperty(
            component, target, consumed_args, filename, lineno)

      except FireError as error:
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

  if show_completion:
    if name is None:
      raise ValueError('Cannot make completion script without command name')
    script = CompletionScript(name, initial_component)
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
  members = dict(inspect.getmembers(component))
  arg = args[0]
  arg_names = [
      arg,
      arg.replace('-', '_'),  # treat '-' as '_'.
  ]

  for arg_name in arg_names:
    if arg_name in members:
      return members[arg_name], [arg], args[1:]

  raise FireError('Could not consume arg:', arg)


def _CallCallable(fn, args):
  """Calls the function fn by consuming args from args.

  Args:
    fn: The function to call or class to instantiate.
    args: Args from which to consume for calling the function.
  Returns:
    component: The object that is the result of the function call.
    consumed_args: The args that were consumed for the function call.
    remaining_args: The remaining args that haven't been consumed yet.
    capacity: Whether the call could have taken additional args.
  """
  parse = _MakeParseFn(fn)
  (varargs, kwargs), consumed_args, remaining_args, capacity = parse(args)

  result = fn(*varargs, **kwargs)
  return result, consumed_args, remaining_args, capacity


def _MakeParseFn(fn):
  """Creates a parse function for fn.

  Args:
    fn: The function or class to create the parse function for.
  Returns:
    A parse function for fn. The parse function accepts a list of arguments
    and returns (varargs, kwargs), remaining_args. The original function fn
    can then be called with fn(*varargs, **kwargs). The remaining_args are
    the leftover args from the arguments to the parse function.
  """
  fn_spec = inspectutils.GetFullArgSpec(fn)
  all_args = fn_spec.args + fn_spec.kwonlyargs
  metadata = decorators.GetMetadata(fn)

  # Note: num_required_args is the number of positional arguments without
  # default values. All of these arguments are required.
  num_required_args = len(fn_spec.args) - len(fn_spec.defaults)
  required_kwonly = set(fn_spec.kwonlyargs) - set(fn_spec.kwonlydefaults)

  def _ParseFn(args):
    """Parses the list of `args` into (varargs, kwargs), remaining_args."""
    kwargs, remaining_kwargs, remaining_args = _ParseKeywordArgs(
        args, all_args, fn_spec.varkw)

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
    FireError: if additional positional arguments are expected, but none are
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


def _ParseKeywordArgs(args, fn_args, fn_keywords):
  """Parses the supplied arguments for keyword arguments.

  Given a list of arguments, finds occurences of --name value, and uses 'name'
  as the keyword and 'value' as the value. Constructs and returns a dictionary
  of these keyword arguments, and returns a list of the remaining arguments.

  Only if fn_keywords is None, this only finds argument names used by the
  function, specified through fn_args.

  This returns the values of the args as strings. They are later processed by
  _ParseArgs, which converts them to the appropriate type.

  Args:
    args: A list of arguments
    fn_args: A list of argument names that the target function accepts,
        including positional and named arguments, but not the varargs or kwargs
        names.
    fn_keywords: The argument name for **kwargs, or None if **kwargs not used
  Returns:
    kwargs: A dictionary mapping keywords to values.
    remaining_kwargs: A list of the unused kwargs from the original args.
    remaining_args: A list of the unused arguments from the original args.
  """
  kwargs = {}
  remaining_kwargs = []
  remaining_args = []

  if not args:
    return kwargs, remaining_kwargs, remaining_args

  skip_argument = False

  for index, argument in enumerate(args):
    if skip_argument:
      skip_argument = False
      continue

    arg_consumed = False
    if argument.startswith('--'):
      # This is a named argument; get its value from this arg or the next.
      got_argument = False

      keyword = argument[2:]
      contains_equals = '=' in keyword
      is_bool_syntax = (
          not contains_equals and
          (index + 1 == len(args) or args[index + 1].startswith('--')))
      if contains_equals:
        keyword, value = keyword.split('=', 1)
        got_argument = True
      elif is_bool_syntax:
        # Since there's no next arg or the next arg is a Flag, we consider
        # this flag to be a boolean.
        got_argument = True
        if keyword in fn_args:
          value = 'True'
        elif keyword.startswith('no'):
          keyword = keyword[2:]
          value = 'False'
        else:
          value = 'True'
      else:
        if index + 1 < len(args):
          value = args[index + 1]
          got_argument = True

      keyword = keyword.replace('-', '_')

      # In order for us to consume the argument as a keyword arg, we either:
      # Need to be explicitly expecting the keyword, or we need to be
      # accepting **kwargs.
      if got_argument:
        skip_argument = not contains_equals and not is_bool_syntax
        arg_consumed = True
        if keyword in fn_args or fn_keywords:
          kwargs[keyword] = value
        else:
          remaining_kwargs.append(argument)
          if skip_argument:
            remaining_kwargs.append(args[index + 1])

    if not arg_consumed:
      # The argument was not consumed, so it is still a remaining argument.
      remaining_args.append(argument)

  return kwargs, remaining_kwargs, remaining_args


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
