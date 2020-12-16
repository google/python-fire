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

# Lint as: python3
"""This module has components that use Python 3 specific syntax."""

import asyncio
import functools
from typing import Tuple


# pylint: disable=keyword-arg-before-vararg
def identity(arg1, arg2: int, arg3=10, arg4: int = 20, *arg5,
             arg6, arg7: int, arg8=30, arg9: int = 40, **arg10):
  return arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10


class KeywordOnly(object):

  def double(self, *, count):
    return count * 2

  def triple(self, *, count):
    return count * 3

  def with_default(self, *, x="x"):
    print("x: " + x)


class LruCacheDecoratedMethod(object):

  @functools.lru_cache()
  def lru_cache_in_class(self, arg1):
    return arg1


@functools.lru_cache()
def lru_cache_decorated(arg1):
  return arg1


class WithAsyncio(object):

  @asyncio.coroutine
  def double(self, count=0):
    return 2 * count


class WithTypes(object):
  """Class with functions that have default arguments and types."""

  def double(self, count: float) -> float:
    """Returns the input multiplied by 2.

    Args:
      count: Input number that you want to double.

    Returns:
      A number that is the double of count.s
    """
    return 2 * count

  def long_type(
      self,
      long_obj: (Tuple[Tuple[Tuple[Tuple[Tuple[Tuple[Tuple[
          Tuple[Tuple[Tuple[Tuple[Tuple[int]]]]]]]]]]]])
  ):
    return long_obj


class WithDefaultsAndTypes(object):
  """Class with functions that have default arguments and types."""

  def double(self, count: float = 0) -> float:
    """Returns the input multiplied by 2.

    Args:
      count: Input number that you want to double.

    Returns:
      A number that is the double of count.s
    """
    return 2 * count

  def get_int(self, value: int = None):
    return 0 if value is None else value
