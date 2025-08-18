# Python Fire [![PyPI](https://img.shields.io/pypi/pyversions/fire.svg?style=plastic)](https://github.com/google/python-fire)

_Python Fire is a library for automatically generating command line interfaces
(CLIs) from absolutely any Python object._

-   Python Fire is a simple way to create a CLI in Python.
    [[1]](docs/benefits.md#simple-cli)
-   Python Fire is a helpful tool for developing and debugging Python code.
    [[2]](docs/benefits.md#debugging)
-   Python Fire helps with exploring existing code or turning other people's
    code into a CLI. [[3]](docs/benefits.md#exploring)
-   Python Fire makes transitioning between Bash and Python easier.
    [[4]](docs/benefits.md#bash)
-   Python Fire makes using a Python REPL easier by setting up the REPL with the
    modules and variables you'll need already imported and created.
    [[5]](docs/benefits.md#repl)

## Installation

Create 'Virtual Environment' first. Visit the [Python official documentation](https://docs.python.org/3/tutorial/venv.html). After creating the virtual environment, you can proceed with the installation of Python Fire within that environment.

To install Python Fire with pip, run: `pip install fire`

To install Python Fire with conda, run: `conda install fire -c conda-forge`

To install Python Fire from source, first clone the repository and then run:
`python setup.py install`

## Basic Usage

You can call `Fire` on any Python object:<br>
functions, classes, modules, objects, dictionaries, lists, tuples, etc.
They all work!

Here's an example of calling Fire on a function.

```python
import fire

def hello(name="World"):
  return "Hello %s!" % name

if __name__ == '__main__':
  fire.Fire(hello)
```

Then, from the command line, you can run:

```bash
python hello.py  # Hello World!
python hello.py --name=David  # Hello David!
python hello.py --help  # Shows usage information.
```

Here's an example of calling Fire on a class.

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
about Fire's other features, see the [Using a Fire CLI page](docs/using-cli.md).

For additional examples, see [The Python Fire Guide](docs/guide.md).

## Why is it called Fire?

When you call `Fire`, it fires off (executes) your command.

## Where can I learn more?

Please see [The Python Fire Guide](docs/guide.md).

## Reference

| Setup   | Command             | Notes
| :------ | :------------------ | :---------
| install | `pip install fire`  |

| Creating a CLI | Command                | Notes
| :--------------| :--------------------- | :---------
| import         | `import fire`          |
| Call           | `fire.Fire()`          | Turns the current module into a Fire CLI.
| Call           | `fire.Fire(component)` | Turns `component` into a Fire CLI.

| Using a CLI                                     | Command                                 | Notes
| :---------------------------------------------- | :-------------------------------------- | :----
| [Help](docs/using-cli.md#help-flag)             | `command --help` or `command -- --help` |
| [REPL](docs/using-cli.md#interactive-flag)      | `command -- --interactive`              | Enters interactive mode.
| [Separator](docs/using-cli.md#separator-flag)   | `command -- --separator=X`              | Sets the separator to `X`. The default separator is `-`.
| [Completion](docs/using-cli.md#completion-flag) | `command -- --completion [shell]`       | Generates a completion script for the CLI.
| [Trace](docs/using-cli.md#trace-flag)           | `command -- --trace`                    | Gets a Fire trace for the command.
| [Verbose](docs/using-cli.md#verbose-flag)       | `command -- --verbose`                  |

_Note that these flags are separated from the Fire command by an isolated `--`._

## License

Licensed under the
[Apache 2.0](https://github.com/google/python-fire/blob/master/LICENSE) License.

## Disclaimer

This is not an official Google product.
