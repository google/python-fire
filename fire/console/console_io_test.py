# Copyright 2026 Google LLC. All Rights Reserved.
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

"""Tests for console_io.py."""

import io
import os
import signal
from unittest import mock

from fire import core
from fire import testutils
from fire.console import console_io


class MoreTest(testutils.BaseTestCase):

  def setUp(self):
    super().setUp()
    original_handler = signal.getsignal(signal.SIGINT)
    self.addCleanup(signal.signal, signal.SIGINT, original_handler)
    self.handler = mock.Mock()
    signal.signal(signal.SIGINT, self.handler)
    self.out = io.StringIO()
    self.process = mock.Mock()
    self.process.communicate.side_effect = self.AssertSigintIgnored
    self.process.wait.side_effect = self.AssertSigintIgnored
    self.StartPatch(mock.patch.dict(os.environ, {'PAGER': 'test-pager'}))
    self.interactive = self.StartPatch(
        mock.patch.object(console_io, 'IsInteractive', return_value=True))
    self.popen = self.StartPatch(mock.patch.object(
        console_io.subprocess, 'Popen', side_effect=self.StartPager))
    self.attr = self.StartPatch(
        mock.patch.object(console_io.console_attr, 'GetConsoleAttr'))
    self.attr.return_value.GetEncoding.return_value = 'utf-8'
    self.find = self.StartPatch(
        mock.patch.object(console_io.files, 'FindExecutableOnPath'))
    self.internal = self.StartPatch(
        mock.patch.object(console_io.console_pager, 'Pager'))

  def StartPatch(self, patcher):
    self.addCleanup(patcher.stop)
    return patcher.start()

  def AssertSigintIgnored(self, **_kwargs):
    self.assertEqual(signal.getsignal(signal.SIGINT), signal.SIG_IGN)

  def StartPager(self, *_args, **_kwargs):
    self.AssertSigintIgnored()
    return self.process

  def testRestoresSigintAfterExternalPager(self):
    for handler in (self.handler, signal.default_int_handler,
                    signal.SIG_DFL, signal.SIG_IGN):
      for pager in ('test-pager', 'less', 'pager'):
        with self.subTest(handler=handler, pager=pager):
          signal.signal(signal.SIGINT, handler)
          os.environ['PAGER'] = pager if pager == 'test-pager' else ''
          self.find.side_effect = lambda command, selected=pager: (
              command == selected)
          console_io.More('example', self.out)
          self.assertEqual(signal.getsignal(signal.SIGINT), handler)
          self.popen.assert_called_with(
              pager, stdin=console_io.subprocess.PIPE, shell=True)
          self.process.communicate.assert_called_with(input=b'example')
          self.internal.assert_not_called()

  def testRestoresSigintOnPagerError(self):
    for target, error in (
        (self.popen, OSError('spawn')),
        (self.attr, ValueError('encoding lookup')),
        (self.process.communicate, OSError('communicate')),
        (self.process.wait, OSError('wait')),
        (self.process.communicate, KeyboardInterrupt())):
      with self.subTest(error=error):
        signal.signal(signal.SIGINT, self.handler)
        original_effect = target.side_effect
        target.side_effect = error
        try:
          with self.assertRaises(type(error)) as caught:
            console_io.More('example', self.out)
        finally:
          target.side_effect = original_effect
        self.assertIs(caught.exception, error)
        self.assertEqual(signal.getsignal(signal.SIGINT), self.handler)
        self.internal.assert_not_called()

  def testRestoresSigintOnEncodingError(self):
    self.attr.return_value.GetEncoding.return_value = 'ascii'
    with self.assertRaises(UnicodeEncodeError):
      console_io.More('\u00e9', self.out)
    self.assertEqual(signal.getsignal(signal.SIGINT), self.handler)
    self.process.communicate.assert_not_called()

  def testNoninteractivePreservesSigint(self):
    self.interactive.return_value = False
    console_io.More('example', self.out)
    self.assertEqual(self.out.getvalue(), 'example')
    self.assertEqual(signal.getsignal(signal.SIGINT), self.handler)
    self.popen.assert_not_called()
    self.internal.assert_not_called()

  def testInternalPagerPreservesSigint(self):
    for check_pager, pager in ((False, 'test-pager'), (True, '-'), (True, '')):
      with self.subTest(check_pager=check_pager, pager=pager):
        os.environ['PAGER'] = pager
        self.find.return_value = None
        console_io.More('example', self.out, check_pager=check_pager)
        self.assertEqual(signal.getsignal(signal.SIGINT), self.handler)
        self.popen.assert_not_called()
        self.internal.assert_called_with('example', self.out, None)
        self.internal.return_value.Run.assert_called_with()

  def testDisplayPreservesSigint(self):
    core.Display(['first', 'second'], self.out)
    self.assertEqual(signal.getsignal(signal.SIGINT), self.handler)
    self.process.communicate.assert_called_once_with(input=b'first\nsecond\n')


if __name__ == '__main__':
  testutils.main()
