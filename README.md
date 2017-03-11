# Python Fire
_Python Fire is a library for creating command line interfaces (CLIs) from
absolutely any Python object._

- Python Fire is a simple way to create a CLI in Python. [[1]](doc/benefits.md#simple-cli)
- Python Fire is a helpful tool for developing and debugging Python code. [[2]](doc/benefits.md#debugging)
- Python Fire helps with exploring existing code or turning other people's code
into a CLI. [[3]](doc/benefits.md#exploring)
- Python Fire makes transitioning between Bash and Python easier. [[4]](doc/benefits.md#bash)
- Python Fire makes using a Python REPL easier by setting up the REPL with the
modules and variables you'll need already imported and created. [[5]](doc/benefits.md#repl)


## Installation

`pip install fire`


## Basic Usage

You can call `Fire` on any Python object:<br>
functions, classes, modules, objects, dictionaries, lists, tuples, etc.
They all work!

Here's a simple example.

```python
import fire

class Calculator(object):
  """A simple calculator class."""

  def double(self, number):
    return 2 * number

if __name__ == '__main__':
  fire.Fire(Calculator)
```

Then, from the command line, you can run:

```bash
python calculator.py double 10  # 20
python calculator.py double --number=15  # 30
```

To learn how Fire behaves on functions, objects, dicts, lists, etc, and to learn
about Fire's other features, see the [Using a Fire CLI page](doc/using-cli.md).

For additional examples, see [The Python Fire Guide](doc/guide.md).


## Why is it called Fire?

When you call `Fire`, it fires off (executes) your command.


## Where can I learn more?

Please see [The Python Fire Guide](doc/guide.md).


## Reference

| Setup   | Command             | Notes
| :------ | :------------------ | :---------
| install | `pip install fire`  |

| Creating a CLI | Command                | Notes
| :--------------| :--------------------- | :---------
| import         | `import fire`          |
| Call           | `fire.Fire()`          | Turns the current module into a Fire CLI.
| Call           | `fire.Fire(component)` | Turns `component` into a Fire CLI.

| Using a CLI    | Command                    | Notes
| :------------- | :------------------------- | :---------
| [Help](doc/using-cli.md#help-flag) | `command -- --help` |
| [REPL](doc/using-cli.md#interactive-flag) | `command -- --interactive` | Enters interactive mode.
| [Separator](doc/using-cli.md#separator-flag) | `command -- --separator=X` | This sets the separator to `X`. The default separator is `-`.
| [Completion](doc/using-cli.md#completion-flag) | `command -- --completion` | Generate a completion script for the CLI.
| [Trace](doc/using-cli.md#trace-flag) | `command -- --trace` | Gets a Fire trace for the command.
| [Verbose](doc/using-cli.md#verbose-flag) | `command -- --verbose` |
_Note that flags are separated from the Fire command by an isolated `--` arg._


## Disclaimer

This is not an official Google product.
