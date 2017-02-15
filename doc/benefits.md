# Benefits of Python Fire

## Python Fire is a simple way to create a CLI in Python. <a name="simple-cli"></a>

It's dead simple. Simply write the functionality you want exposed at the command
line as a function / module / class, and then call Fire. With this addition of a
single-line call to Fire, your CLI is ready to go.


## Python Fire is a helpful tool for developing and debugging Python code. <a name="debugging"></a>

When you're writing a Python library, you probably want to try it out as you go.
You could write a main method to check the functionality you're interested in,
but then you have to change the main method with every new experiment you're
interested in testing, and constantly updating the main method is a hassle.
You could also open an IPython REPL and import your library there and test it,
but then you have to deal with reloading your imports every time you change
something.

If you simply call Fire in your library, then you can run all of it's
functionality from the command line without having to keep making changes to
a main method. And if you use the `--interactive` flag to enter an IPython REPL
then you don't need to load the imports or create your variables; they'll
already be ready for use as soon as you start the REPL.


## Python Fire helps with exploring existing code or turning other people's code into a CLI. <a name="exploring"></a>

You can take an existing module, maybe even one that you don't have access to
the source code for, and call `Fire` on it. This lets you easily see what
functionality this code exposes, without you having to read through all the
code.

This technique can be a very simple way to create very powerful CLIs. Call
`Fire` on the difflib library and you get a powerful diffing tool. Call `Fire`
on the Python Imaging Library (PIL) module and you get a powerful image
manipulation command line tool, very similar in nature to ImageMagick.

The auto-generated help strings that Fire provides when you run a Fire CLI
allow you to see all the functionality these modules provide in a concise
manner.


## Python Fire makes transitioning between Bash and Python easier. <a name="bash"></a>

Using Fire lets you call Python directly from Bash. So you can mix your Python
functions with the unix tools you know and love, like `grep`, `xargs`, `wc`,
etc.

Additionally since writing CLIs in Python requires only a single call to Fire,
it is now easy to write even one-off scripts that would previously have been in
Bash, in Python.


## Python Fire makes using a Python REPL easier by setting up the REPL with the modules and variables you'll need already imported and created. <a name="repl"></a>

When you use the `--interactive` flag to enter an IPython REPL, it starts with
variables and modules already defined for you. You don't need to waste time
importing the modules you care about or defining the variables you're going to
use, since Fire has already done so for you.
