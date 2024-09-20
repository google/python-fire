## The Python Fire Guide

### Introduction

Welcome to the Python Fire guide! Python Fire is a Python library that will turn
any Python component into a command line interface with just a single call to
`Fire`.

Let's get started!

### Installation

To install Python Fire from pypi, run:

`pip install fire`

Alternatively, to install Python Fire from source, clone the source and run:

`python setup.py install`

### Hello World

##### Version 1: `fire.Fire()`

The easiest way to use Fire is to take any Python program, and then simply call
`fire.Fire()` at the end of the program. This will expose the full contents of
the program to the command line.

```python
import fire

def hello(name):
  return f'Hello {name}!'

if __name__ == '__main__':
  fire.Fire()
```

Here's how we can run our program from the command line:

```bash
$ python example.py hello World
Hello World!
```

##### Version 2: `fire.Fire(<fn>)`

Let's modify our program slightly to only expose the `hello` function to the
command line.

```python
import fire

def hello(name):
  return f'Hello {name}!'

if __name__ == '__main__':
  fire.Fire(hello)
```

Here's how we can run this from the command line:

```bash
$ python example.py World
Hello World!
```

Notice we no longer have to specify to run the `hello` function, because we
called `fire.Fire(hello)`.

##### Version 3: Using a main

We can alternatively write this program like this:

```python
import fire

def hello(name):
  return f'Hello {name}!'

def main():
  fire.Fire(hello)

if __name__ == '__main__':
  main()
```

Or if we're using
[entry points](https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points),
then simply this:

```python
import fire

def hello(name):
  return f'Hello {name}!'

def main():
  fire.Fire(hello)
```

##### Version 4: Fire Without Code Changes

If you have a file `example.py` that doesn't even import fire:

```python
def hello(name):
  return f'Hello {name}!'
```

Then you can use it with Fire like this:

```bash
$ python -m fire example hello --name=World
Hello World!
```

You can also specify the filepath of example.py rather than its module path,
like so:

```bash
$ python -m fire example.py hello --name=World
Hello World!
```

### Exposing Multiple Commands

In the previous example, we exposed a single function to the command line. Now
we'll look at ways of exposing multiple functions to the command line.

##### Version 1: `fire.Fire()`

The simplest way to expose multiple commands is to write multiple functions, and
then call Fire.

```python
import fire

def add(x, y):
  return x + y

def multiply(x, y):
  return x * y

if __name__ == '__main__':
  fire.Fire()
```

We can use this like so:

```bash
$ python example.py add 10 20
30
$ python example.py multiply 10 20
200
```

You'll notice that Fire correctly parsed `10` and `20` as numbers, rather than
as strings. Read more about [argument parsing here](#argument-parsing).

##### Version 2: `fire.Fire(<dict>)`

In version 1 we exposed all the program's functionality to the command line. By
using a dict, we can selectively expose functions to the command line.

```python
import fire

def add(x, y):
  return x + y

def multiply(x, y):
  return x * y

if __name__ == '__main__':
  fire.Fire({
      'add': add,
      'multiply': multiply,
  })
```

We can use this in the same way as before:

```bash
$ python example.py add 10 20
30
$ python example.py multiply 10 20
200
```

##### Version 3: `fire.Fire(<object>)`

Fire also works on objects, as in this variant. This is a good way to expose
multiple commands.

```python
import fire

class Calculator(object):

  def add(self, x, y):
    return x + y

  def multiply(self, x, y):
    return x * y

if __name__ == '__main__':
  calculator = Calculator()
  fire.Fire(calculator)
```

We can use this in the same way as before:

```bash
$ python example.py add 10 20
30
$ python example.py multiply 10 20
200
```


##### Version 4: `fire.Fire(<class>)`

Fire also works on classes. This is another good way to expose multiple
commands.

```python
import fire

class Calculator(object):

  def add(self, x, y):
    return x + y

  def multiply(self, x, y):
    return x * y

if __name__ == '__main__':
  fire.Fire(Calculator)
```

We can use this in the same way as before:

```bash
$ python example.py add 10 20
30
$ python example.py multiply 10 20
200
```

Why might you prefer a class over an object? One reason is that you can pass
arguments for constructing the class too, as in this broken calculator example.

```python
import fire

class BrokenCalculator(object):

  def __init__(self, offset=1):
      self._offset = offset

  def add(self, x, y):
    return x + y + self._offset

  def multiply(self, x, y):
    return x * y + self._offset

if __name__ == '__main__':
  fire.Fire(BrokenCalculator)
```

When you use a broken calculator, you get wrong answers:

```bash
$ python example.py add 10 20
31
$ python example.py multiply 10 20
201
```

But you can always fix it:

```bash
$ python example.py add 10 20 --offset=0
30
$ python example.py multiply 10 20 --offset=0
200
```

Unlike calling ordinary functions, which can be done both with positional
arguments and named arguments (--flag syntax), arguments to \_\_init\_\_
functions must be passed with the --flag syntax. See the section on
[calling functions](#calling-functions) for more.

### Grouping Commands

Here's an example of how you might make a command line interface with grouped
commands.

```python
class IngestionStage(object):

  def run(self):
    return 'Ingesting! Nom nom nom...'

class DigestionStage(object):

  def run(self, volume=1):
    return ' '.join(['Burp!'] * volume)

  def status(self):
    return 'Satiated.'

class Pipeline(object):

  def __init__(self):
    self.ingestion = IngestionStage()
    self.digestion = DigestionStage()

  def run(self):
    ingestion_output = self.ingestion.run()
    digestion_output = self.digestion.run()
    return [ingestion_output, digestion_output]

if __name__ == '__main__':
  fire.Fire(Pipeline)
```

Here's how this looks at the command line:

```bash
$ python example.py run
Ingesting! Nom nom nom...
Burp!
$ python example.py ingestion run
Ingesting! Nom nom nom...
$ python example.py digestion run
Burp!
$ python example.py digestion status
Satiated.
```

You can nest your commands in arbitrarily complex ways, if you're feeling grumpy
or adventurous.


### Accessing Properties

In the examples we've looked at so far, our invocations of `python example.py`
have all run some function from the example program. In this example, we simply
access a property.

```python
from airports import airports

import fire

class Airport(object):

  def __init__(self, code):
    self.code = code
    self.name = dict(airports).get(self.code)
    self.city = self.name.split(',')[0] if self.name else None

if __name__ == '__main__':
  fire.Fire(Airport)
```

Now we can use this program to learn about airport codes!

```bash
$ python example.py --code=JFK code
JFK
$ python example.py --code=SJC name
San Jose-Sunnyvale-Santa Clara, CA - Norman Y. Mineta San Jose International (SJC)
$ python example.py --code=ALB city
Albany-Schenectady-Troy
```

By the way, you can find this
[airports module here](https://github.com/trendct-data/airports.py).

### Chaining Function Calls

When you run a Fire CLI, you can take all the same actions on the _result_ of
the call to Fire that you can take on the original object passed in.

For example, we can use our Airport CLI from the previous example like this:

```bash
$ python example.py --code=ALB city upper
ALBANY-SCHENECTADY-TROY
```

This works since `upper` is a method on all strings.

So, if you want to set up your functions to chain nicely, all you have to do is
have a class whose methods return self. Here's an example.

```python
import fire

class BinaryCanvas(object):
  """A canvas with which to make binary art, one bit at a time."""

  def __init__(self, size=10):
    self.pixels = [[0] * size for _ in range(size)]
    self._size = size
    self._row = 0  # The row of the cursor.
    self._col = 0  # The column of the cursor.

  def __str__(self):
    return '\n'.join(' '.join(str(pixel) for pixel in row) for row in self.pixels)

  def show(self):
    print(self)
    return self

  def move(self, row, col):
    self._row = row % self._size
    self._col = col % self._size
    return self

  def on(self):
    return self.set(1)

  def off(self):
    return self.set(0)

  def set(self, value):
    self.pixels[self._row][self._col] = value
    return self

if __name__ == '__main__':
  fire.Fire(BinaryCanvas)
```

Now we can draw stuff :).

```bash
$ python example.py move 3 3 on move 3 6 on move 6 3 on move 6 6 on move 7 4 on move 7 5 on
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 1 0 0 1 0 0 0
0 0 0 0 1 1 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
```

It's supposed to be a smiley face.

### Custom Serialization

You'll notice in the BinaryCanvas example, the canvas with the smiley face was
printed to the screen. You can determine how a component will be serialized by
defining its `__str__` method.

If a custom `__str__` method is present on the final component, the object is
serialized and printed. If there's no custom `__str__` method, then the help
screen for the object is shown instead.

### Can we make an even simpler example than Hello World?

Yes, this program is even simpler than our original Hello World example.

```python
import fire
english = 'Hello World'
spanish = 'Hola Mundo'
fire.Fire()
```

You can use it like this:

```bash
$ python example.py english
Hello World
$ python example.py spanish
Hola Mundo
```

### Calling Functions

Arguments to a constructor are passed by name using flag syntax `--name=value`.

For example, consider this simple class:

```python
import fire

class Building(object):

  def __init__(self, name, stories=1):
    self.name = name
    self.stories = stories

  def climb_stairs(self, stairs_per_story=10):
    for story in range(self.stories):
      for stair in range(1, stairs_per_story):
        yield stair
      yield 'Phew!'
    yield 'Done!'

if __name__ == '__main__':
  fire.Fire(Building)
```

We can instantiate it as follows: `python example.py --name="Sherrerd Hall"`

Arguments to other functions may be passed positionally or by name using flag
syntax.

To instantiate a `Building` and then run the `climb_stairs` function, the
following commands are all valid:

```bash
$ python example.py --name="Sherrerd Hall" --stories=3 climb_stairs 10
$ python example.py --name="Sherrerd Hall" climb_stairs --stairs_per_story=10
$ python example.py --name="Sherrerd Hall" climb_stairs --stairs-per-story 10
$ python example.py climb-stairs --stairs-per-story 10 --name="Sherrerd Hall"
```

You'll notice that hyphens and underscores (`-` and `_`) are interchangeable in
member names and flag names.

You'll also notice that the constructor's arguments can come after the
function's arguments or before the function.

You'll also notice that the equal sign between the flag name and its value is
optional.

##### Functions with `*varargs` and `**kwargs`

Fire supports functions that take \*varargs or \*\*kwargs. Here's an example:

```python
import fire

def order_by_length(*items):
  """Orders items by length, breaking ties alphabetically."""
  sorted_items = sorted(items, key=lambda item: (len(str(item)), str(item)))
  return ' '.join(sorted_items)

if __name__ == '__main__':
  fire.Fire(order_by_length)
```

To use it, we run:

```bash
$ python example.py dog cat elephant
cat dog elephant
```

You can use a separator to indicate that you're done providing arguments to a
function. All arguments after the separator will be used to process the result
of the function, rather than being passed to the function itself. The default
separator is the hyphen `-`.

Here's an example where we use a separator.

```bash
$ python example.py dog cat elephant - upper
CAT DOG ELEPHANT
```

Without the separator, upper would have been treated as another argument.

```bash
$ python example.py dog cat elephant upper
cat dog upper elephant
```

You can change the separator with the `--separator` flag. Flags are always
separated from your Fire command by an isolated `--`. Here's an example where we
change the separator.

```bash
$ python example.py dog cat elephant X upper -- --separator=X
CAT DOG ELEPHANT
```

Separators can be useful when a function accepts \*varargs, \*\*kwargs, or
default values that you don't want to specify. It is also important to remember
to change the separator if you want to pass `-` as an argument.


##### Async Functions

Fire supports calling async functions too. Here's a simple example.

```python
import asyncio

async def count_to_ten():
  for i in range(1, 11):
    await asyncio.sleep(1)
    print(i)

if __name__ == '__main__':
  fire.Fire(count_to_ten)
```

Whenever fire encounters a coroutine function, it runs it, blocking until it completes.


### Argument Parsing

The types of the arguments are determined by their values, rather than by the
function signature where they're used. You can pass any Python literal from the
command line: numbers, strings, tuples, lists, dictionaries, (sets are only
supported in some versions of Python). You can also nest the collections
arbitrarily as long as they only contain literals.

To demonstrate this, we'll make a small example program that tells us the type
of any argument we give it:

```python
import fire
fire.Fire(lambda obj: type(obj).__name__)
```

And we'll use it like so:

```bash
$ python example.py 10
int
$ python example.py 10.0
float
$ python example.py hello
str
$ python example.py '(1,2)'
tuple
$ python example.py [1,2]
list
$ python example.py True
bool
$ python example.py {name:David}
dict
```

You'll notice in that last example that bare-words are automatically replaced
with strings.

Be careful with your quotes! If you want to pass the string `"10"`, rather than
the int `10`, you'll need to either escape or quote your quotes. Otherwise Bash
will eat your quotes and pass an unquoted `10` to your Python program, where
Fire will interpret it as a number.


```bash
$ python example.py 10
int
$ python example.py "10"
int
$ python example.py '"10"'
str
$ python example.py "'10'"
str
$ python example.py \"10\"
str
```

Be careful with your quotes! Remember that Bash processes your arguments first,
and then Fire parses the result of that.
If you wanted to pass the dict `{"name": "David Bieber"}` to your program, you
might try this:

```bash
$ python example.py '{"name": "David Bieber"}'  # Good! Do this.
dict
$ python example.py {"name":'"David Bieber"'}  # Okay.
dict
$ python example.py {"name":"David Bieber"}  # Wrong. This is parsed as a string.
str
$ python example.py {"name": "David Bieber"}  # Wrong. This isn't even treated as a single argument.
<error>
$ python example.py '{"name": "Justin Bieber"}'  # Wrong. This is not the Bieber you're looking for. (The syntax is fine though :))
dict
```

##### Boolean Arguments

The tokens `True` and `False` are parsed as boolean values.

You may also specify booleans via flag syntax `--name` and `--noname`, which set
`name` to `True` and `False` respectively.

Continuing the previous example, we could run any of the following:

```bash
$ python example.py --obj=True
bool
$ python example.py --obj=False
bool
$ python example.py --obj
bool
$ python example.py --noobj
bool
```

Be careful with boolean flags! If a token other than another flag immediately
follows a flag that's supposed to be a boolean, the flag will take on the value
of the token rather than the boolean value. You can resolve this: by putting a
separator after your last flag, by explicitly stating the value of the boolean
flag (as in `--obj=True`), or by making sure there's another flag after any
boolean flag argument.


### Using Fire Flags

Fire CLIs all come with a number of flags. These flags should be separated from
the Fire command by an isolated `--`. If there is at least one isolated `--`
argument, then arguments after the final isolated `--` are treated as flags,
whereas all arguments before the final isolated `--` are considered part of the
Fire command.

One useful flag is the `--interactive` flag. Use the `--interactive` flag on any
CLI to enter a Python REPL with all the modules and variables used in the
context where `Fire` was called already available to you for use. Other useful
variables, such as the result of the Fire command will also be available. Use
this feature like this: `python example.py -- --interactive`.

You can add the help flag to any command to see help and usage information. Fire
incorporates your docstrings into the help and usage information that it
generates. Fire will try to provide help even if you omit the isolated `--`
separating the flags from the Fire command, but may not always be able to, since
`help` is a valid argument name. Use this feature like this: `python
example.py -- --help` or `python example.py --help` (or even `python example.py
-h`).

The complete set of flags available is shown below, in the reference section.


### Reference

| Setup   | Command             | Notes
| :------ | :------------------ | :---------
| install | `pip install fire`  |

##### Creating a CLI

| Creating a CLI | Command                | Notes
| :--------------| :--------------------- | :---------
| import         | `import fire`          |
| Call           | `fire.Fire()`          | Turns the current module into a Fire CLI.
| Call           | `fire.Fire(component)` | Turns `component` into a Fire CLI.

##### Flags

| Using a CLI    | Command                    | Notes
| :------------- | :------------------------- | :---------
| [Help](using-cli.md#help-flag) | `command -- --help` | Show help and usage information for the command.
| [REPL](using-cli.md#interactive-flag) | `command -- --interactive` | Enter interactive mode.
| [Separator](using-cli.md#separator-flag) | `command -- --separator=X` | This sets the separator to `X`. The default separator is `-`.
| [Completion](using-cli.md#completion-flag) | `command -- --completion [shell]` | Generate a completion script for the CLI.
| [Trace](using-cli.md#trace-flag) | `command -- --trace` | Gets a Fire trace for the command.
| [Verbose](using-cli.md#verbose-flag) | `command -- --verbose` | Include private members in the output.

_Note that flags are separated from the Fire command by an isolated `--` arg.
Help is an exception; the isolated `--` is optional for getting help._


##### Arguments for Calling fire.Fire()

| Argument  | Usage                     | Notes                                |
| --------- | ------------------------- | ------------------------------------ |
| component | `fire.Fire(component)`    | If omitted, defaults to a dict of all locals and globals. |
| command   | `fire.Fire(command='hello --name=5')` | Either a string or a list of arguments. If a string is provided, it is split to determine the arguments. If a list or tuple is provided, they are the arguments. If `command` is omitted, then `sys.argv[1:]` (the arguments from the command line) are used by default. |
| name      | `fire.Fire(name='tool')`  | The name of the CLI, ideally the name users will enter to run the CLI. This name will be used in the CLI's help screens. If the argument is omitted, it will be inferred automatically.|
| serialize | `fire.Fire(serialize=custom_serializer)` | If omitted, simple types are serialized via their builtin str method, and any objects that define a custom `__str__` method are serialized with that. If specified, all objects are serialized to text via the provided method. |


### Disclaimer

Python Fire is not an official Google product.
