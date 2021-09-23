## Python Fire Quick Reference

| Setup   | Command             | Notes
| :------ | :------------------ | :---------
| install | `pip install fire`  |

| Creating a CLI | Command                | Notes
| :--------------| :--------------------- | :---------
| import         | `import fire`          |
| Call           | `fire.Fire()`          | Turns the current module into a Fire CLI.
| Call           | `fire.Fire(component)` | Turns `component` into a Fire CLI.

| Using a CLI                                | Command        | Notes          |
| :----------------------------------------- | :------------- | :------------- |
| [Help](using-cli.md#help-flag)             | `command       | Show the help  |
:                                            : --help`        : screen.        :
| [REPL](using-cli.md#interactive-flag)      | `command --    | Enters         |
:                                            : --interactive` : interactive    :
:                                            :                : mode.          :
| [Separator](using-cli.md#separator-flag)   | `command --    | This sets the  |
:                                            : --separator=X` : separator to   :
:                                            :                : `X`. The       :
:                                            :                : default        :
:                                            :                : separator is   :
:                                            :                : `-`.           :
| [Completion](using-cli.md#completion-flag) | `command --    | Generate a     |
:                                            : --completion   : completion     :
:                                            : [shell]`       : script for the :
:                                            :                : CLI.           :
| [Trace](using-cli.md#trace-flag)           | `command --    | Gets a Fire    |
:                                            : --trace`       : trace for the  :
:                                            :                : command.       :
| [Verbose](using-cli.md#verbose-flag)       | `command --    |                |
:                                            : --verbose`     :                :

_Note that flags are separated from the Fire command by an isolated `--` arg.
Help is an exception; the isolated `--` is optional for getting help._

## Arguments for Calling fire.Fire()

| Argument  | Usage                     | Notes                                |
| :-------- | :------------------------ | :----------------------------------- |
| component | `fire.Fire(component)`    | If omitted, defaults to a dict of    |
:           :                           : all locals and globals.              :
| command   | `fire.Fire(command='hello | Either a string or a list of         |
:           : --name=5')`               : arguments. If a string is provided,  :
:           :                           : it is split to determine the         :
:           :                           : arguments. If a list or tuple is     :
:           :                           : provided, they are the arguments. If :
:           :                           : `command` is omitted, then           :
:           :                           : `sys.argv[1\:]` (the arguments from  :
:           :                           : the command line) are used by        :
:           :                           : default.                             :
| name      | `fire.Fire(name='tool')`  | The name of the CLI, ideally the     |
:           :                           : name users will enter to run the     :
:           :                           : CLI. This name will be used in the   :
:           :                           : CLI's help screens. If the argument  :
:           :                           : is omitted, it will be inferred      :
:           :                           : automatically.                       :

## Using a Fire CLI without modifying any code

You can use Python Fire on a module without modifying the code of the module.
The syntax for this is:

`python -m fire <module> <arguments>`

or

`python -m fire <filepath> <arguments>`

For example, `python -m fire calendar -h` will treat the built in `calendar`
module as a CLI and provide its help.
