# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for fire.console.console_io."""

import io
from unittest import mock

from fire import testutils
from fire.console import console_io


class MoreTest(testutils.BaseTestCase):

  @mock.patch.object(console_io, 'IsInteractive', return_value=True)
  @mock.patch.object(console_io.signal, 'signal')
  @mock.patch.object(console_io.encoding, 'GetEncodedValue')
  @mock.patch.object(console_io.subprocess, 'Popen')
  def testMoreDoesNotUseShellForPager(
      self, mock_popen, mock_get_encoded_value, unused_mock_signal,
      unused_mock_is_interactive):
    # Regression test: PAGER must never be passed through a shell, since a
    # malicious or attacker-controlled PAGER value could otherwise inject
    # arbitrary commands (CWE-78).
    mock_get_encoded_value.side_effect = (
        lambda env, name, default=None: {
            'PAGER': 'less -R; touch /tmp/pwned',
        }.get(name, default)
    )
    mock_process = mock.Mock()
    mock_process.communicate.return_value = (b'', b'')
    mock_popen.return_value = mock_process

    console_io.More('some contents', io.StringIO())

    pager_calls = [
        call for call in mock_popen.call_args_list
        if call.args and call.args[0][:1] == ['less']
    ]
    self.assertEqual(len(pager_calls), 1)
    args, kwargs = pager_calls[0]
    self.assertFalse(kwargs.get('shell'))
    self.assertEqual(args[0], ['less', '-R;', 'touch', '/tmp/pwned'])


if __name__ == '__main__':
  testutils.main()
