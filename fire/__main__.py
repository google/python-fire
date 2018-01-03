"""
Module for running python fire as a "main" function and thereby allowing using
fire with other programs.
"""
import importlib
import sys

import fire

def main():
  module_name = sys.argv[1]
  module = importlib.import_module(module_name)
  fire.Fire(module, name=module_name, command=sys.argv[2:])

if __name__ == '__main__':
  main()
