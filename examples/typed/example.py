#!/usr/bin/python3
from __future__ import annotations

import typing
import fire
import urllib.parse
import pathlib
from pathlib import Path

class TestTyped(object):
    def test(
        self,
        digitString: str,
        path1: pathlib.Path,
        path2: 'pathlib.Path',
        # path3: Path, # Not Support
        regexp: typing.Pattern,
        url: urllib.parse.ParseResult,
    ):
        assert(str == type(digitString))
        assert(digitString.isdigit())
        print(path1.as_uri())
        print(path2.as_uri())
        print(regexp.findall('1234567890'))
        print(url.netloc)
        
def main():
    fire.Fire(TestTyped())

if __name__ == "__main__":
    main()
