# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""These decorators provide function metadata to Python Fire.

SetParseFn and SetParseFns allow you to set the functions Fire uses for parsing
command line arguments to client code.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from functools import wraps
from logging import (getLogger, RootLogger, StreamHandler, FileHandler,
                    Formatter, DEBUG, INFO, WARNING, ERROR)

from exceptions import InvalidLogLevel
import inspect

FIRE_METADATA = 'FIRE_METADATA'
FIRE_PARSE_FNS = 'FIRE_PARSE_FNS'
ACCEPTS_POSITIONAL_ARGS = 'ACCEPTS_POSITIONAL_ARGS'


def SetParseFn(fn, *arguments):
  """Sets the fn for Fire to use to parse args when calling the decorated fn.

  Args:
    fn: The function to be used for parsing arguments.
    *arguments: The arguments for which to use the parse fn. If none are listed,
      then this will set the default parse function.
  Returns:
    The decorated function, which now has metadata telling Fire how to perform.
  """
  def _Decorator(func):
    parse_fns = GetParseFns(func)
    if not arguments:
      parse_fns['default'] = fn
    else:
      for argument in arguments:
        parse_fns['named'][argument] = fn
    _SetMetadata(func, FIRE_PARSE_FNS, parse_fns)
    return func

  return _Decorator


def SetParseFns(*positional, **named):
  """Set the fns for Fire to use to parse args when calling the decorated fn.

  Returns a decorator, which when applied to a function adds metadata to the
  function telling Fire how to turn string command line arguments into proper
  Python arguments with which to call the function.

  A parse function should accept a single string argument and return a value to
  be used in it's place when calling the decorated function.

  Args:
    *positional: The functions to be used for parsing positional arguments.
    **named: The functions to be used for parsing named arguments.
  Returns:
    The decorated function, which now has metadata telling Fire how to perform.
  """
  def _Decorator(fn):
    parse_fns = GetParseFns(fn)
    parse_fns['positional'] = positional
    parse_fns['named'].update(named)
    _SetMetadata(fn, FIRE_PARSE_FNS, parse_fns)
    return fn

  return _Decorator


def _SetMetadata(fn, attribute, value):
  metadata = GetMetadata(fn)
  metadata[attribute] = value
  setattr(fn, FIRE_METADATA, metadata)


def GetMetadata(fn):
  default = {
      ACCEPTS_POSITIONAL_ARGS: not inspect.isclass(fn),
  }
  return getattr(fn, FIRE_METADATA, default)


def GetParseFns(fn):
  metadata = GetMetadata(fn)
  default = dict(default=None, positional=[], named={})
  return metadata.get(FIRE_PARSE_FNS, default)


def logger(level: str='DEBUG', log_file: bool=False, log_name: str='fire.log',
           formatter: str=Formatter(('%(levelname)s - %(filename)s - %(asctime)s '
                                     '- %(message)s - line: %(lineno)d'))):
    """
    Decorator to add logs to functions.

    param: level (optional)
        - receives the desired level of the log as a string.
        default: 'DEBUG'

    param: log_file (optional)
        - receives a boolean value indicating whether there will be a log file
          or not.
        default: False

    param: log_name (optional)
        - receives a name for the log file.
        default: 'fire.log'

    param: formatter (optional)
        - receives a formatting for the log output.
        default: '%(levelname)s - %(filename)s - %(asctime)s - %(message)s - %(lineno)d'
        example:
            DEBUG - your_file.py - 2019-05-20 15:28:42,635 - There was an exception in foo() - line: 160
    """

    level = level.strip().upper()
    log_levels = {
                'DEBUG': DEBUG, 'INFO': INFO, 'WARNING': WARNING,
                'ERROR': ERROR
                }

    def _file_handler():
        file_handler = FileHandler(log_name)
        file_handler.setLevel(log_levels[level])
        file_handler.setFormatter(formatter)
        return file_handler


    def _console_handler():
        console_handler = StreamHandler()
        console_handler.setLevel(log_levels[level])
        console_handler.setFormatter(formatter)
        return console_handler


    def _add_logger(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            if level in log_levels:
                logger = getLogger()
                logger.setLevel(log_levels[level])

                try:
                    return func(*args)
                except:
                    message = 'There was an exception in {0}()'.format(func.__name__)
                    logger.addHandler(_file_handler()) if log_file else None
                    logger.addHandler(_console_handler())

                    logger.debug(message) if level == 'DEBUG' else None
                    logger.info(message) if level == 'INFO' else None
                    logger.warning(message) if level == 'WARNING' else None
                    logger.error(message) if level == 'ERROR' else None
                    raise
            else:
                raise InvalidLogLevel('The log level value is invalid.')
        return _inner
    return _add_logger
