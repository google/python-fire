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

"""Tests for environment variable configuration support."""

import os
from unittest import mock

from fire import core
from fire import testutils


class EnvVarTest(testutils.BaseTestCase):

  def testEnvVarConfig(self):
    def fn(arg1, arg2=10):
      return arg1, arg2

    # Without env vars, it should fail if required arg is missing.
    with self.assertRaisesFireExit(2, 'The function received no value for the required argument: arg1'):
      core.Fire(fn, command=[])

    # With env var for arg1.
    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'hello'}):
      self.assertEqual(core.Fire(fn, command=[]), ('hello', 10))

    # With env var for arg2.
    with mock.patch.dict(os.environ, {'FIRE_ARG2': '20'}):
      # Note: it will still fail for arg1 if missing.
      with self.assertRaisesFireExit(2, 'The function received no value for the required argument: arg1'):
        core.Fire(fn, command=[])

      # Now provide arg1 on CLI.
      self.assertEqual(core.Fire(fn, command=['hi']), ('hi', 20))

    # Env var for both.
    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'val1', 'FIRE_ARG2': 'val2'}):
      self.assertEqual(core.Fire(fn, command=[]), ('val1', 'val2'))

    # Command line overrides env var.
    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'env1', 'FIRE_ARG2': 'env2'}):
      self.assertEqual(core.Fire(fn, command=['cli1']), ('cli1', 'env2'))
      self.assertEqual(core.Fire(fn, command=['--arg2=cli2']), ('env1', 'cli2'))

  def testEnvVarWithUnderscores(self):
    def fn(my_arg, another_arg=1):
      return my_arg, another_arg

    with mock.patch.dict(os.environ, {'FIRE_MY_ARG': 'val1', 'FIRE_ANOTHER_ARG': 'val2'}):
      self.assertEqual(core.Fire(fn, command=[]), ('val1', 'val2'))

  def testEnvVarWithKwonly(self):
    def fn(*, arg1, arg2=10):
      return arg1, arg2

    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'hello'}):
      self.assertEqual(core.Fire(fn, command=[]), ('hello', 10))

    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'v1', 'FIRE_ARG2': 'v2'}):
      self.assertEqual(core.Fire(fn, command=[]), ('v1', 'v2'))
      self.assertEqual(core.Fire(fn, command=['--arg2=v3']), ('v1', 'v3'))

  def testEnvVarWithVarkw(self):
    def fn(**kwargs):
      return kwargs

    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'val1', 'FIRE_ARG2': 'val2'}):
      self.assertEqual(core.Fire(fn, command=[]), {'arg1': 'val1', 'arg2': 'val2'})

  def testEnvVarTypes(self):
    def fn(arg1):
      return arg1, type(arg1)

    # Boolean
    with mock.patch.dict(os.environ, {'FIRE_ARG1': 'True'}):
      self.assertEqual(core.Fire(fn, command=[]), (True, bool))

    # Integer
    with mock.patch.dict(os.environ, {'FIRE_ARG1': '123'}):
      self.assertEqual(core.Fire(fn, command=[]), (123, int))

    # List
    with mock.patch.dict(os.environ, {'FIRE_ARG1': '[1, 2, 3]'}):
      self.assertEqual(core.Fire(fn, command=[]), ([1, 2, 3], list))

    # Dict
    with mock.patch.dict(os.environ, {'FIRE_ARG1': '{"a": 1}'}):
      self.assertEqual(core.Fire(fn, command=[]), ({'a': 1}, dict))

if __name__ == '__main__':
  testutils.main()
