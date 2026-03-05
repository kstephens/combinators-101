from typing import Any, Optional, Union, List, Tuple, Dict, Iterable, Mapping, Callable, Type, Literal, IO, NoReturn, Self
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
import inspect
from icecream import ic
from http import HTTPStatus
# from abc import abstractclass


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

# Functions with zero or more arguments that return anything.
Variadic = Callable[..., Any]

# Functions with zero or more arguments that return a boolean.
Predicate = Callable[..., bool]


def identity(x):
  return x

# This forces map to list:
map_ = map
def map(*args, **kwargs):
   return list(map_(*args, **kwargs))

def reduce(f: Binary, xs: Iterable, init: Any) -> Any:
  'Returns the result of `init = f(x, init)` for each element `x` in `xs`.'
  for x in xs:
    init = f(init, x)
  return init

def compose(*callables) -> Variadic:
  """
  Returns the composition one or more functions, in reverse order.
  For example, `compose(g, f)(x, y)` is equivalent to `g(f(x, y))`.
  """
  f: Callable = callables[-1]
  gs: Iterable[Unary] = tuple(reversed(callables[:-1]))
  def h(*args, **kwargs):
    result = f(*args, **kwargs)
    for g in gs:
      result = g(result)
    return result
  return h


def combinator(c):
    "Renames c and its result for human eyes."
    def g(*args, **kwargs):
        f = c(*args, **kwargs)
        if callable(f):
            args_ = args_str(args, kwargs)
            f.__name__ = f"{c.__name__}{args_}"
            f.__qualname__ = f"{c.__qualname__}{args_}"
        return f
    g.__name__ = c.__name__
    g.__qualname__ = c.__qualname__
    return g


def args_str(args, kwargs):
    max_len = 30
    def r(x):
        if callable(x):
            return f"{x.__module__}.{x.__qualname__}"
        return str_limit(repr(x), 10)
    s = f"(" + ', '.join([r(x) for x in args] + [f"{r(k)}={r(v)}" for k, v in kwargs.items()]) + ")"
    return str_limit(s, max_len)

def str_limit(s, max_len):
    # ic((s, len(s), max_len))
    if len(s) > max_len:
        # left, right = s[:max_len], s[:-max_len]
        left, right = s[:max_len], s
        nest_left = nest_right = 0
        for c in left:
            if c in '({[':
                nest_left += 1
            elif c in ']})':
                nest_left -= 1
        for c in reversed(right):
            # ic((c, nest_left, nest_right))
            if not nest_left:
                break
            if c not in ']})':
                break
            nest_right += 1
            nest_left -= 1
        nest_right = -nest_right - 1
        # ic((nest_left, nest_right))
        s = f"{s[:max_len]}...{s[nest_right:]}"
    return s

# def str_limit(s, max_len):
#     if len(s) > max_len:
#         s = f"{s[:max_len]}...{s[-1]}"
#     return s


#####################################
# See combinators_101.ipynb

def format_args(name, args, kwargs):
    return f"{name}(" + ', '.join([repr(x) for x in args] + [f"{k!r}={v!r}" for k, v in kwargs.items()]) + ")"

#####################################

color_ = "\033[0m"
color_r = "\033[38;2;200;50;50m"
color_g = "\033[38;2;40;180;40m"
color_b = "\033[38;2;120;120;255m"
trace_indent = 0                                             # <-- GLOBAL STATE

def trace(f: Callable, name: str | None = None) -> Callable:
    "Wrap a function that logs input and output."
    name = name or f.__name__                                # <-- LOCAL STATE
    def g(*args, **kwargs):                                  # <-- COMPOSITION
        global trace_indent                                  # <-- GLOBAL STATE
        ind = f"\u21e2 {"\u2502 " * trace_indent}"
        print(f"{color_g}{ind}{color_}{format_args(name, args, kwargs)}")
        try:
            # Increase indent:
            trace_indent += 1
            result = f(*args, **kwargs)                      # <--- APPLICATION
        except Exception as exc:
            print(f"{color_r}{ind}\u2570\u2574\u29b8 {exc!r}{color_}")
            raise exc
        finally:
            # Decrease indent:
            trace_indent -= 1
        print(f"{color_b}{ind}\u2570\u2574{color_} {color_b}{result!r}{color_}")
        return result                                        # <--- RESULT
    return g                                                 # <--- CLOSURE

####################################


def re_pred(pat: str, re_func: Callable = re.search) -> Predicate:
  'Returns a predicate that matches a regular expression.'
  rx = re.compile(pat)
  return lambda x: re_func(rx, str(x)) is not None


def http_status_line(code: int) -> str:
    try:
        return f"{code} {HTTPStatus(code).phrase}"
    except ValueError:
        return str(code)

# def export_to(env):
#     env.update(globals())


####################################

