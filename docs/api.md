## Python Fire Quick Reference

| Setup   | Command             | Notes
| ------- | ------------------- | ----------
| install | `pip install fire`  | Installs fire from pypi

| Creating a CLI | Command                | Notes
| ---------------| ---------------------- | ----------
| import         | `import fire`          |
| Call           | `fire.Fire()`          | Turns the current module into a Fire CLI.
| Call           | `fire.Fire(component)` | Turns `component` into a Fire CLI.

| Using a CLI                                | Command                           | Notes          |
| ------------------------------------------ | -----------------                 | -------------- |
| [Help](using-cli.md#help-flag)             | `command --help`                  | Show the help screen. |
| [REPL](using-cli.md#interactive-flag)      | `command -- --interactive`        | Enters interactive mode. |
| [Separator](using-cli.md#separator-flag)   | `command -- --separator=X`        | This sets the separator to `X`. The default separator is `-`. |
| [Completion](using-cli.md#completion-flag) | `command -- --completion [shell]` | Generate a completion script for the CLI. |
| [Trace](using-cli.md#trace-flag)           | `command -- --trace`              | Gets a Fire trace for the command. |
| [Verbose](using-cli.md#verbose-flag)       | `command -- --verbose`            |                |

_Note that flags are separated from the Fire command by an isolated `--` arg.
Help is an exception; the isolated `--` is optional for getting help._

## Arguments for Calling fire.Fire()

| Argument  | Usage                     | Notes                                |
| --------- | ------------------------- | ------------------------------------ |
| component | `fire.Fire(component)`    | If omitted, defaults to a dict of all locals and globals. |
| command   | `fire.Fire(command='hello --name=5')` | Either a string or a list of arguments. If a string is provided, it is split to determine the arguments. If a list or tuple is provided, they are the arguments. If `command` is omitted, then `sys.argv[1:]` (the arguments from the command line) are used by default. |
| name      | `fire.Fire(name='tool')`  | The name of the CLI, ideally the name users will enter to run the CLI. This name will be used in the CLI's help screens. If the argument is omitted, it will be inferred automatically.|
| serialize | `fire.Fire(serialize=custom_serializer)` | If omitted, simple types are serialized via their builtin str method, and any objects that define a custom `__str__` method are serialized with that. If specified, all objects are serialized to text via the provided method. |

## Using a Fire CLI without modifying any code

You can use Python Fire on a module without modifying the code of the module.
The syntax for this is:

`python -m fire <module> <arguments>`

or

`python -m fire <filepath> <arguments>`

For example, `python -m fire calendar -h` will treat the built in `calendar`
module as a CLI and provide its help.
