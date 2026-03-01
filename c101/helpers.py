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


def reduce(f: Binary, init: Any, xs: Sequence) -> Sequence:
  'Returns the result of `init = f(x, init)` for each element `x` in `xs`.'
  for x in xs:
    init = f(init, x)
  return init


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
