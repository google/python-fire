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

PYTHON_VERSION=${PYTHON_VERSION:-3.7}

pip install -U -r .github/scripts/requirements.txt
python setup.py develop
python -m pytest  # Run the tests without IPython.
pip install ipython
python -m pytest  # Now run the tests with IPython.
pylint fire --ignore=test_components_py3.py,parser_fuzz_test.py,console
if [[ ${PYTHON_VERSION} == 3.7 ]]; then
  # Run type-checking.
  pip install pytype;
  pytype -x fire/test_components_py3.py;
fi
