# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple time utilities Fire CLI.

This example demonstrates exposing simple time helper functions using Fire.
Fire() is called with no target component so all functions in this module
become CLI commands.

Example usage:
  time_tools now
  time_tools to-seconds 1 30
  time_tools add-seconds "2024-01-01 10:00:00" 120
"""

import fire
import datetime


def now():
  """Return the current datetime as a string."""
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_seconds(minutes=0, seconds=0):
  """Return minutes + seconds converted to total seconds."""
  return minutes * 60 + seconds


def add_seconds(time_string="", seconds=0):
  """Add seconds to a datetime string."""
  dt = datetime.datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
  new_dt = dt + datetime.timedelta(seconds=seconds)
  return new_dt.strftime("%Y-%m-%d %H:%M:%S")


def main():
  fire.Fire(name="time_tools")


if __name__ == "__main__":
  main()
