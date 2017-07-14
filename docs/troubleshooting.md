# Troubleshooting

This page describes known issues that users of Python Fire have run into. If you
have an issue not resolved here, consider opening a
[GitHub Issue](https://github.com/google/python-fire/issues).

### Issue [#19](https://github.com/google/python-fire/issues/19): Don't name your module "cmd"

If you have a module name that conflicts with the name of a builtin module, then
when Fire goes to import the builtin module, it will import your module instead.
This will result in an error, possibly an `AttributeError`. Specifically, do not
name your module any of the following:
sys, linecache, cmd, bdb, repr, os, re, pprint, traceback
