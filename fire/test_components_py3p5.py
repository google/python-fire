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
"""This module has components that use Python 3.5 specific syntax."""


from typing import Tuple

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
