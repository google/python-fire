#!/usr/bin/env python
"""Run fire on the given module or file

Usage: fire [-m module] [-f file] [fire-style arguments to desired python object]

Example:

$ fire -m random Random gauss 3 4
5.056813212816271

Documentation on fire:
 https://github.com/google/python-fire/blob/master/doc/guide.md

Discussion: https://github.com/google/python-fire/issues/29
"""

import fire
import imp
import sys

if __name__ == '__main__':
    if sys.argv[1] == '-m':
        (fileobj, pathname, description) = imp.find_module(sys.argv[2])
        module = imp.load_module('module', fileobj, pathname, description)
        sys.argv = sys.argv[2:]
    elif sys.argv[1] == '-f':
        module = imp.load_source('module', sys.argv[2])
        sys.argv = sys.argv[2:]
    else:
        print("Usage: fire [-m module] [-f file] [fire-style arguments to desired python object]")
        sys.exit(1)

    from module import *

    fire.Fire()
