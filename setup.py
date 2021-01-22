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

"""The setup.py file for Python Fire."""

from setuptools import setup

LONG_DESCRIPTION = """
Python Fire is a library for automatically generating command line interfaces
(CLIs) with a single line of code.

It will turn any Python module, class, object, function, etc. (any Python
component will work!) into a CLI. It's called Fire because when you call Fire(),
it fires off your command.
""".strip()

SHORT_DESCRIPTION = """
A library for automatically generating command line interfaces.""".strip()

DEPENDENCIES = [
    'six',
    'termcolor',
    'enum34; python_version < "3.4"'
]

TEST_DEPENDENCIES = [
    'hypothesis',
    'mock',
    'python-Levenshtein',
]

VERSION = '0.4.0'
URL = 'https://github.com/google/python-fire'

setup(
    name='fire',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,

    author='David Bieber',
    author_email='dbieber@google.com',
    license='Apache Software License',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
    ],

    keywords='command line interface cli python fire interactive bash tool',

    packages=['fire', 'fire.console'],

    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
)
