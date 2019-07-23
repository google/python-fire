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

"""Custom descriptions and summaries for the builtin types.

The docstrings for objects of primitive types reflect the type of the object,
rather than the object itself. For example, the docstring for any dict is this:

> print({'key': 'value'}.__doc__)
dict() -> new empty dictionary
dict(mapping) -> new dictionary initialized from a mapping object's
    (key, value) pairs
dict(iterable) -> new dictionary initialized as if via:
    d = {}
    for k, v in iterable:
        d[k] = v
dict(**kwargs) -> new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)

As you can see, this docstring is more pertinant to the function `dict` and
would be suitable as the result of `dict.__doc__`, but is wholely unsuitable
as a description for the dict `{'key': 'value'}`.

This modules aims to resolve that problem, providing custom summaries and
descriptions for primitive typed values.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six


def NeedsCustomDescription(component):
  """Whether the component should use a custom description and summary.

  Components of primitive type, such as ints, floats, dicts, lists, and others
  have messy builtin docstrings. These are inappropriate for display as
  descriptions and summaries in a CLI. This function determines whether the
  provided component has one of these docstrings.

  Note that an object such as `int` has the same docstring as an int like `3`.
  The docstring is OK for `int`, but is inappropriate as a docstring for `3`.

  Args:
    component: The component of interest.
  Returns:
    Whether the component should use a custom description and summary.
  """
  type_ = type(component)
  if (type_ in six.string_types
      or type_ in six.integer_types
      or type_ is six.text_type
      or type_ is six.binary_type
      or type_ in (float, complex, bool)
      or type_ in (dict, tuple, list, set, frozenset)
     ):
    return True
  return False
