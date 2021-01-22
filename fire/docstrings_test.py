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

"""Tests for fire docstrings module."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from fire import docstrings
from fire import testutils

# pylint: disable=invalid-name
DocstringInfo = docstrings.DocstringInfo
ArgInfo = docstrings.ArgInfo
KwargInfo = docstrings.KwargInfo
# pylint: enable=invalid-name


class DocstringsTest(testutils.BaseTestCase):

  def test_one_line_simple(self):
    docstring = """A simple one line docstring."""
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='A simple one line docstring.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_one_line_simple_whitespace(self):
    docstring = """
      A simple one line docstring.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='A simple one line docstring.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_one_line_too_long(self):
    # pylint: disable=line-too-long
    docstring = """A one line docstring thats both a little too verbose and a little too long so it keeps going well beyond a reasonable length for a one-liner.
    """
    # pylint: enable=line-too-long
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='A one line docstring thats both a little too verbose and '
        'a little too long so it keeps going well beyond a reasonable length '
        'for a one-liner.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_one_line_runs_over(self):
    # pylint: disable=line-too-long
    docstring = """A one line docstring thats both a little too verbose and a little too long
    so it runs onto a second line.
    """
    # pylint: enable=line-too-long
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='A one line docstring thats both a little too verbose and '
        'a little too long so it runs onto a second line.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_one_line_runs_over_whitespace(self):
    docstring = """
      A one line docstring thats both a little too verbose and a little too long
      so it runs onto a second line.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='A one line docstring thats both a little too verbose and '
        'a little too long so it runs onto a second line.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_google_format_args_only(self):
    docstring = """One line description.

    Args:
      arg1: arg1_description
      arg2: arg2_description
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='One line description.',
        args=[
            ArgInfo(name='arg1', description='arg1_description'),
            ArgInfo(name='arg2', description='arg2_description'),
        ]
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_google_format_arg_named_args(self):
    docstring = """
    Args:
      args: arg_description
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        args=[
            ArgInfo(name='args', description='arg_description'),
        ]
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_google_format_typed_args_and_returns(self):
    docstring = """Docstring summary.

    This is a longer description of the docstring. It spans multiple lines, as
    is allowed.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is a longer description of the docstring. It spans '
        'multiple lines, as\nis allowed.',
        args=[
            ArgInfo(name='param1', type='int',
                    description='The first parameter.'),
            ArgInfo(name='param2', type='str',
                    description='The second parameter.'),
        ],
        returns='bool: The return value. True for success, False otherwise.'
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_google_format_multiline_arg_description(self):
    docstring = """Docstring summary.

    This is a longer description of the docstring. It spans multiple lines, as
    is allowed.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter. This has a lot of text, enough to
        cover two lines.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is a longer description of the docstring. It spans '
        'multiple lines, as\nis allowed.',
        args=[
            ArgInfo(name='param1', type='int',
                    description='The first parameter.'),
            ArgInfo(name='param2', type='str',
                    description='The second parameter. This has a lot of text, '
                                'enough to cover two lines.'),
        ],
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_rst_format_typed_args_and_returns(self):
    docstring = """Docstring summary.

    This is a longer description of the docstring. It spans across multiple
    lines.

    :param arg1: Description of arg1.
    :type arg1: str.
    :param arg2: Description of arg2.
    :type arg2: bool.
    :returns:  int -- description of the return value.
    :raises: AttributeError, KeyError
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is a longer description of the docstring. It spans '
        'across multiple\nlines.',
        args=[
            ArgInfo(name='arg1', type='str',
                    description='Description of arg1.'),
            ArgInfo(name='arg2', type='bool',
                    description='Description of arg2.'),
        ],
        returns='int -- description of the return value.',
        raises='AttributeError, KeyError',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_numpy_format_typed_args_and_returns(self):
    docstring = """Docstring summary.

    This is a longer description of the docstring. It spans across multiple
    lines.

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is a longer description of the docstring. It spans '
        'across multiple\nlines.',
        args=[
            ArgInfo(name='param1', type='int',
                    description='The first parameter.'),
            ArgInfo(name='param2', type='str',
                    description='The second parameter.'),
        ],
        # TODO(dbieber): Support return type.
        returns='bool True if successful, False otherwise.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_numpy_format_multiline_arg_description(self):
    docstring = """Docstring summary.

    This is a longer description of the docstring. It spans across multiple
    lines.

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter. This has a lot of text, enough to cover two
        lines.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is a longer description of the docstring. It spans '
        'across multiple\nlines.',
        args=[
            ArgInfo(name='param1', type='int',
                    description='The first parameter.'),
            ArgInfo(name='param2', type='str',
                    description='The second parameter. This has a lot of text, '
                                'enough to cover two lines.'),
        ],
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_multisection_docstring(self):
    docstring = """Docstring summary.

    This is the first section of a docstring description.

    This is the second section of a docstring description. This docstring
    description has just two sections.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        description='This is the first section of a docstring description.'
        '\n\n'
        'This is the second section of a docstring description. This docstring'
        '\n'
        'description has just two sections.',
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_google_section_with_blank_first_line(self):
    docstring = """Inspired by requests HTTPAdapter docstring.

    :param x: Simple param.

    Usage:

      >>> import requests
    """
    docstring_info = docstrings.parse(docstring)
    self.assertEqual('Inspired by requests HTTPAdapter docstring.',
                     docstring_info.summary)

  def test_ill_formed_docstring(self):
    docstring = """Docstring summary.

    args: raises ::
    :
    pathological docstrings should not fail, and ideally should behave
    reasonably.
    """
    docstrings.parse(docstring)

  def test_strip_blank_lines(self):
    lines = ['   ', '  foo  ', '   ']
    expected_output = ['  foo  ']

    self.assertEqual(expected_output, docstrings._strip_blank_lines(lines))  # pylint: disable=protected-access

  def test_numpy_colon_in_description(self):
    docstring = """
     Greets name.

     Arguments
     ---------
     name : str
         name, default : World
     arg2 : int
         arg2, default:None
     arg3 : bool
     """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Greets name.',
        description=None,
        args=[
            ArgInfo(name='name', type='str',
                    description='name, default : World'),
            ArgInfo(name='arg2', type='int',
                    description='arg2, default:None'),
            ArgInfo(name='arg3', type='bool', description=None),
        ]
    )
    self.assertEqual(expected_docstring_info, docstring_info)

  def test_rst_format_typed_args_and_kwargs(self):
    docstring = """Docstring summary.

    :param arg1: Description of arg1.
    :type arg1: str.
    :key arg2: Description of arg2.
    :type arg2: bool.
    :key arg3: Description of arg3.
    :type arg3: str.
    """
    docstring_info = docstrings.parse(docstring)
    expected_docstring_info = DocstringInfo(
        summary='Docstring summary.',
        args=[
            ArgInfo(name='arg1', type='str',
                    description='Description of arg1.'),
            KwargInfo(name='arg2', type='bool',
                      description='Description of arg2.'),
            KwargInfo(name='arg3', type='str',
                      description='Description of arg3.'),
        ],
    )
    self.assertEqual(expected_docstring_info, docstring_info)


if __name__ == '__main__':
  testutils.main()
