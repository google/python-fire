# Using a Fire CLI

## Basic usage

Every Fire command corresponds to a Python component.

The simplest Fire command consists of running your program with no additional
arguments. This command corresponds to the Python component you called the
`Fire` function on. If you did not supply an object in the call to `Fire`, then
the context in which `Fire` was called will be used as the Python component.

You can append `--help` or `-h` to a command to see what Python component it
corresponds to, as well as the various ways in which you can extend the command.

Flags to Fire should be separated from the Fire command by an isolated `--` in
order to distinguish between flags and named arguments. So, for example, to
enter interactive mode append `-- -i` or `-- --interactive` to any command. To
use Fire in verbose mode, append `-- --verbose`.

Given a Fire command that corresponds to a Python object, you can extend that
command to access a member of that object, call it with arguments if it is a
function, instantiate it if it is a class, or index into it if it is a list.

Read on to learn about how you can write a Fire command corresponding to
whatever Python component you're looking for.


### Accessing members of an object

If your command corresponds to an object, you can extend your command by adding
the name of a member of that object as a new argument to the command. The
resulting command will correspond to that member.

For example, if the object your command corresponds to has a method defined on
it named 'whack', then you can add the argument 'whack' to your command, and the
resulting new command corresponds to the whack method.

As another example, if the object your command corresponds to has a property
named high_score, then you can add the argument 'high-score' to your command,
and the resulting new command corresponds to the value of the high_score
property.


### Accessing members of a dict

If your command corresponds to a dict, you can extend your command by adding
the name of one of the dict's keys as an argument.

For example, `widget function-that-returns-dict key` will correspond to the
value of the item with key `key` in the dict returned by
`function_that_returns_dict`.


### Accessing members of a list or tuple

If your command corresponds to a list or tuple, you can extend your command by
adding the index of an element of the component to your command as an argument.

For example, `widget function-that-returns-list 2` will correspond to item 2 of
the result of `function_that_returns_list`.


### Calling a function

If your command corresponds to a function, you can extend your command by adding
the arguments of this function. Arguments can be specified positionally, or by
name. To specify an argument by name, use flag syntax.

For example, suppose your `command` corresponds to the function `double`:

```python
def double(value=0):
  return 2 * value
```

Then you can extend your command using named arguments as `command --value 5`,
or using positional arguments as `command 5`. In both cases, the new command
corresponds to the result of the function, in this case the number 10.

You can force a function that takes a variable number of arguments to be
evaluated by adding a separator (the default separator is the hyphen, "-"). This
will prevent arguments to the right of the separator from being consumed for
calling the function. This is useful if the function has arguments with default
values, or if the function accepts \*varargs, or if the function accepts
\*\*kwargs.

See also the section on [Changing the Separator](#separator-flag).


### Instantiating a class

If your command corresponds to a class, you can extend your command by adding
the arguments of the class's `__init__` function. Arguments must be specified
by name, using the flags syntax. See the section on
[calling a function](#calling-a-function) for more details.

Similarly, when passing arguments to a callable object (an object with a custom
`__call__` function), those arguments must be passed using flags syntax.

## Using Flags with Fire CLIs <a name="using-flags"></a>

Command line arguments to a Fire CLI are normally consumed by Fire, as described
in the [Basic Usage](#basic-usage) section. In order to set Flags, put the flags
after the final standalone `--` argument. (If there is no `--` argument, then no
arguments are used for flags.)

For example, to set the alsologtostderr flag, you could run the command:
`widget bang --noise=boom -- --alsologtostderr`. The `--noise` argument is
consumed by Fire, but the `--alsologtostderr` argument is treated as a normal
Flag.

All CLIs built with Python Fire share some flags, as described in the next
sections.


## Python Fire's Flags

As described in the [Using Flags](#using-flags) section, you must add an
isolated `--` argument in order to have arguments treated as Flags rather than
be consumed by Python Fire. All arguments to a Fire CLI after the final
standalone `--` argument are treated as Flags.

The following flags are accepted by all Fire CLIs:
[`--interactive`/`-i`](#interactive-flag),
[`--help`/`-h`](#help-flag),
[`--separator`](#separator-flag),
[`--completion`](#completion-flag),
[`--trace`](#trace-flag),
and [`--verbose`/`-v`](#verbose-flag),
as described in the following sections.

### `--interactive`: Interactive mode <a name="interactive-flag"></a>

Call `widget -- --interactive` or `widget -- -i` to enter interactive mode. This
will put you in an IPython REPL, with the variable `widget` already defined.

You can then explore the Python object that `widget` corresponds to
interactively using Python.

Note: if you want fire to start the IPython REPL instead of the regular Python one,
the `ipython` package needs to be installed in your environment.


### `--completion`: Generating a completion script <a name="completion-flag"></a>

Call `widget -- --completion` to generate a completion script for the Fire CLI
`widget`. To save the completion script to your home directory, you could e.g.
run `widget -- --completion > ~/.widget-completion`. You should then source this
file; to get permanent completion, source this file from your `.bashrc` file.

Call `widget -- --completion fish` to generate a completion script for the Fish
shell. Source this file from your fish.config.

If the commands available in the Fire CLI change, you'll have to regenerate the
completion script and source it again.


### `--help`: Getting help <a name="help-flag"></a>

Let say you have a command line tool named `widget` that was made with Fire. How
do you use this Fire CLI?

The simplest way to get started is to run `widget -- --help`. This will give you
usage information for your CLI. You can always append `-- --help` to any Fire
command in order to get usage information for that command and any subcommands.

Additionally, help will be displayed if you hit an error using Fire. For
example, if you try to pass too many or too few arguments to a function, then
help will be displayed. Similarly, if you try to access a member that does not
exist, or if you index into a list with too high an index, then help will be
displayed.

The displayed help shows information about which Python component your command
corresponds to, as well as usage information for how to extend that command.


### `--trace`: Getting a Fire trace <a name="trace-flag"></a>

In order to understand what is happening when you call Python Fire, it can be
useful to request a trace. This is done via the `--trace` flag, e.g.
`widget whack 5 -- --trace`.

A trace provides step by step information about how the Fire command was
executed. In includes which actions were taken, starting with the initial
component, leading to the final component represented by the command.

A trace is also shown alongside the help if your Fire command reaches an error.


### `--separator`: Changing the separator <a name="separator-flag"></a>

As described in [Calling a Function](#calling-a-function), you can use a
separator argument when writing a command that corresponds to calling a
function. The separator will cause the function to be evaluated or the class to
be instantiated using only the arguments left of the separator. Arguments right
of the separator will then be applied to the result of the function call or to
the instantiated object.

The default separator is `-`.

If you want to supply the string "-" as an argument, then you will have to
change the separator. You can choose a new separator by supplying the
`--separator` flag to Fire.

Here's an example to demonstrate separator usage. Let's say you have a function
that takes a variable number of args, and you want to call that function, and
then upper case the result. Here's how to do it:

```python
# Here's the Python function
def display(arg1, arg2='!'):
  return arg1 + arg2
```

```bash
# Here's what you can do from Bash (Note: the default separator is the hyphen -)
display hello                         # hello!
display hello upper                   # helloupper
display hello - upper                 # HELLO!
display - SEP upper -- --separator SEP    # -!
```
Notice how in the third and fourth lines, the separator caused the display
function to be called with the default value for arg2. In the fourth example,
we change the separator to the string "SEP" so that we can pass '-' as an
argument.

### `--verbose`: Verbose usage <a name="verbose-flag"></a>

Adding the `-v` or `--verbose` flag turns on verbose mode. This will eg
reveal private members in the usage string. Often these members will not
actually be usable from the command line tool. As such, verbose mode should be
considered a debugging tool, but not fully supported yet.
