from typing import Any, Optional, Union, List, Tuple, Dict, Iterable, Mapping, Callable, Type, Literal, IO
from numbers import Number
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from pprint import pprint
from types import FunctionType
from io import StringIO
import re
import sys
import logging
import functools
import math
from pprint import pformat
import dis
from icecream import ic
ic.configureOutput(prefix="  #>> ")
#ic.configureOutput(includeContext=True)

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

trace_indent = 0
def trace(f: Callable, name: str | None = None) -> Callable:
    "Wrap a function that logs input and output."
    name= name or f.__name__                                 # <-- LOCAL STATE
    def g(*args, **kwargs):                                  # <-- COMPOSITION
        global trace_indent                                  # <-- GLOBAL STATE
        indent = f"\u21e2 {"\u2502 " * trace_indent}"
        print(f"{indent}{format_args(name, args, kwargs)}")
        try:
            trace_indent += 1
            result = f(*args, **kwargs)                      # <--- APPLICATION
        finally:
            trace_indent -= 1
        print(f"{indent}\u2570\u2574 {result!r}")
        return result                                        # <--- RESULT
    return g                                                 # <--- CLOSURE


def format_args(name, args, kwargs):
    return f"{name}(" + ', '.join([repr(x) for x in args] + [f"{k!r}={v!r}" for k, v in kwargs.items()]) + ")"


# def export_to(env):
#     env.update(globals())
