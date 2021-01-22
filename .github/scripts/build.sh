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

#!/usr/bin/env bash

# Exit when any command fails.
set -e

PYTHON_VERSION=${PYTHON_VERSION:-2.7}

pip install --upgrade setuptools pip
pip install --upgrade pylint pytest pytest-pylint pytest-runner
pip install termcolor
pip install hypothesis python-Levenshtein
pip install mock
python setup.py develop
python -m pytest  # Run the tests without IPython.
pip install ipython
python -m pytest  # Now run the tests with IPython.
pylint fire --ignore=test_components_py3.py,parser_fuzz_test.py,console
if [[ ${PYTHON_VERSION} == 2.7 || ${PYTHON_VERSION} == 3.7 ]]; then
  pip install pytype;
fi
# Run type-checking, excluding files that define or use py3 features in py2.
if [[ ${PYTHON_VERSION} == 2.7 ]]; then
  pytype -x \
    fire/fire_test.py \
    fire/inspectutils_test.py \
    fire/test_components_py3.py;
elif [[ ${PYTHON_VERSION} == 3.7 ]]; then
  pytype;
fi

