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

"""Types of values."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect

import six


VALUE_TYPES = (bool, six.string_types, six.integer_types, float, complex)


def IsGroup(component):
  # TODO(dbieber): Check if there are any subcomponents.
  return not IsCommand(component) and not IsValue(component)


def IsCommand(component):
  return inspect.isroutine(component) or inspect.isclass(component)


def IsValue(component):
  return isinstance(component, VALUE_TYPES)
