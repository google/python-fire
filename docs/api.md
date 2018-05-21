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
| [Help](using-cli.md#help-flag) | `command -- --help` |
| [REPL](using-cli.md#interactive-flag) | `command -- --interactive` | Enters interactive mode.
| [Separator](using-cli.md#separator-flag) | `command -- --separator=X` | This sets the separator to `X`. The default separator is `-`.
| [Completion](using-cli.md#completion-flag) | `command -- --completion [shell]` | Generate a completion script for the CLI.
| [Trace](using-cli.md#trace-flag) | `command -- --trace` | Gets a Fire trace for the command.
| [Verbose](using-cli.md#verbose-flag) | `command -- --verbose` |

_Note that flags are separated from the Fire command by an isolated `--` arg._
