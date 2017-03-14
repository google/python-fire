# Copyright (C) 2017 Google Inc.
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

"""This module has components that use Python 3 specific syntax."""


def identity(arg1, arg2: int, arg3=10, arg4: int = 20, *arg5,
             arg6, arg7: int, arg8=30, arg9: int = 40, **arg10):
  return arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10


class KeywordOnly(object):

  def double(self, *, count):
    return count * 2

  def triple(self, *, count):
    return count * 3
