"""
Test using fire via python -m fire
"""
import os

from fire import __main__
from fire import testutils


class MainModuleTest(testutils.BaseTestCase):
  def testNameSetting(self):
    # confirm one of the usage lines has tempfile gettempdir
    with self.assertOutputMatches('tempfile gettempdir'):
      __main__.main(['__main__.py', 'tempfile'])

  def testArgPassing(self):
    expected = os.path.join('part1', 'part2', 'part3')
    with self.assertOutputMatches('%s\n' % expected):
      __main__.main(['__main__.py', 'os.path', 'join', 'part1', 'part2',
                     'part3'])
    with self.assertOutputMatches('%s\n' % expected):
      __main__.main(['__main__.py', 'os', 'path', '-', 'join', 'part1',
                     'part2', 'part3'])
