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

# https://stackoverflow.com/a/47024809/1141958
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def identity(x: Any) -> Any:
  'Returns the first argument.'
  return x

# Function with one argument that returns anything.
Unary = Callable[[Any], Any]

# Functions with two arguments that return anything.
Binary = Callable[[Any, Any], Any]

# Functions with zero or more arguments that return a boolean.
Predicate = Callable[..., bool]


# This forces map to list:
map_ = map
def map(*args, **kwargs):
   return list(map_(*args, **kwargs))

def reduce(f: Binary, xs: Iterable, init: Any) -> Any:
  'Returns the result of `init = f(x, init)` for each element `x` in `xs`.'
  for x in xs:
    init = f(init, x)
  return init


#####################################
# See combinators_101.ipynb

trace_indent = 0                                             # <-- GLOBAL STATE

def trace(f: Callable, name: str | None = None) -> Callable:
    "Wrap a function that logs input and output."
    name = name or f.__name__                                # <-- LOCAL STATE
    def g(*args, **kwargs):                                  # <-- COMPOSITION
        global trace_indent                                  # <-- GLOBAL STATE
        g_, _ = "\033[38;5;22m", "\033[0m"
        g_ = "\033[38;2;40;180;40m"
        b_ = "\033[38;2;120;120;255m"
        ind = f"{g_}\u21e2 {"\u2502 " * trace_indent}"
        print(f"{ind}{_}{format_args(name, args, kwargs)}")
        try:
            trace_indent += 1
            result = f(*args, **kwargs)                      # <--- APPLICATION
        finally:
            trace_indent -= 1
        print(f"{ind}\u2570\u2574{_} {b_}{result!r}{_}")
        return result                                        # <--- RESULT
    return g                                                 # <--- CLOSURE


def format_args(name, args, kwargs):
    return f"{name}(" + ', '.join([repr(x) for x in args] + [f"{k!r}={v!r}" for k, v in kwargs.items()]) + ")"

#####################################


def re_pred(pat: str, re_func: Callable = re.search) -> Predicate:
  'Returns a predicate that matches a regular expression.'
  rx = re.compile(pat)
  return lambda x: re_func(rx, str(x)) is not None


# def export_to(env):
#     env.update(globals())
