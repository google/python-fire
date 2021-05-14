"""Return value parser base on annotation."""

import typing

import re
import sys
import pathlib
import datetime
import urllib.parse
from fire.console import console_io

# # TODO: more complex
# if not typing.TYPE_CHECKING:
#     def reveal_type(x):
#         pass


def generate_parse_fn_annotation(annotation):
    """Return value parser base on annotation."""

    callee = generate_parse_fn_annotation

    parse_fn = None
    if isinstance(annotation, str):
        # case: from __future__ import annotations

        # case: `p:'pathlib.Path'`
        annotation = annotation.strip("'").strip('"')

        special = {}
        if annotation in special:
            # TODO:
            # ReturnType[annotation] .GetFormatter?
            raise NotImplementedError("SpecialAnnotationType")
        else:
            # FIXME
            # desc: cast type string to type
            # eg: 'pathlib.PurePath' -> pathlib.PurePath
            # eg: 'PurePath' -> pathlib.PurePath
            # BOOM: 'PurePath' not in context!
            try:
                # annotation = typing.get_type_hints(fn)[argName]
                annotation = eval(annotation)
            except NameError as e:
                text = """
# If you are using below:
from __future__ import annotations

# change:
from pathlib import Path
# fn(self, x:Path):

# to:
import pathlib
# fn(self, x:pathlib.Path):
"""
                console_io.More(text, out=sys.stderr)
                raise NotImplementedError(f"PartialStringTypeAnnotation: {e}")

            if isinstance(annotation, str):
                # case: avoid endless loop
                raise RecursionError(f"CastAnnotation: {annotation}")
            else:
                return callee(annotation)
    else:
        # case: default
        simple = (
            str,
            int,
            float,
            pathlib.Path,
            pathlib.PosixPath,
            pathlib.WindowsPath,
            pathlib.PurePath,
            pathlib.PurePosixPath,
            pathlib.PureWindowsPath,
        )
        if annotation in simple:
            parse_fn = annotation
        elif annotation == typing.Pattern:
            parse_fn = re.compile
        elif annotation == urllib.parse.ParseResult:
            parse_fn = urllib.parse.urlparse
        elif annotation in (datetime.datetime, datetime.date, datetime.time):
            parse_fn = annotation.fromisoformat

    return parse_fn
