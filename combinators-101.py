#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


# https://stackoverflow.com/questions/17077494/how-do-i-convert-a-ipython-notebook-into-a-python-file-via-commandline
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
map_ = map
reduce_ = functools.reduce

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# https://stackoverflow.com/a/47024809/1141958
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


# # Combinators-101
#
# This workshop is about building functions with functions.
#
# * function types.
# * functions as values.
# * information-hiding with functions.
# * function that create functions.
# * functions that combine functions into new functions.
#
# This workshop presents higher-order functional programming using Python.  While there are other programming which are specifically functional, Python is the most popular programming language in the world and it supports functional programming very well.

# # Types
#
# This workshop will use Python's `typing` framework.  Types help us understand what combinators do with functions.

# ## Basic Types
#
# * `int` - an integer
# * `str` - a string
# * `Any` - any type
# * `List` - a list
# * `List[T]` - a `List` containing values of `T`

# ## Function Types
#
# * `Callable` - anything that can be called with zero or more arguments
# * `Callable[..., T]` - a `Callable` with zero or more arguments that returns a value of type `T`
# * `Callable[[A1, A2], T]` - Two arguments of type `A1` and `A2`, respectively, returning type `T`

# In[ ]:


# Example:
# A `Callable` that has 2 parameters,
#   an `str` and `int`
#   and returns a `Tuple` of `int` and `int`:
Callable[[str, int], Tuple[int, int]]

def h(a: str, b: int) -> Tuple[int, int]:
  return (len(a), len(a) * b)

h("ab", 21)


# # First-Class Functions

# can be:
#
# * assigned to variables
# * arguments to functions
# * returned as values

# ## Functions dont have Names, Names have Functions!

# In[ ]:


print(2)
g = print
g
g(2)


# ## Where did that function come from?

# In[ ]:


def call_func_three_times(func: Callable):
  for x in range(3):
    func(x)

call_func_three_times(print)


# In[ ]:


call_func_three_times(g)


# ## The most useful useless function

# In[ ]:


def identity(x: Any) -> Any:
  'Returns the first argument.'
  return x

identity(2)
h = identity
h
h(3)


# ## Anonymous Functions

# In[ ]:


lambda x: x + 3
(lambda x: x + 3)(2)           # Never had a name.


# In[ ]:


plus_three = lambda x: x + 3   # Gave it a name.
plus_three
plus_three(2)


# # Closures

# * Functions with closure are information hiders.
# * They have access to values that are otherwise not visible outside of them.
# * They "close over variables".

# ## Stateless Closures

# ### Constantly return a value

# In[ ]:


def constantly(val: Any) -> Callable[[], Any]:
  return lambda : val


# In[ ]:


constantly_5 = constantly(5)
constantly_5()
constantly_5()


# In[ ]:


# Fails with arguments
try:
  constantly_5(13, 17)
except Exception as exc:
  exc


# ### A more robust version

# In[ ]:


# Functions with zero or more arguments that return anything.
Variadic = Callable[..., Any]

def constantly(x: Any) -> Variadic:
  'Returns a function that returns a constant value.'
  return lambda *_args, **_kwargs: x

constantly_7 = constantly(7)
constantly_7


# In[ ]:


constantly_7()


# In[ ]:


constantly_7(13, 17)


# ## Adapters

# ### Indexable Getters

# In[ ]:


# Function with one argument that returns anything.
Unary = Callable[[Any], Any]

# A value `x` that supports `x[i]`:
Indexable = Union[List, Tuple, Dict]


# In[ ]:


def at(i: Any) -> Unary:
  'Returns a function `f(x)` that returns `x[i]`.'
  return lambda x: x[i]

a = ['a', 'b', 'c', 'd']
f = at(2)
f(a)


# In[ ]:


def indexed(x: Indexable) -> Unary:
  'Returns a function `f(i)` that returns `x[i]`.'
  return lambda i: x[i]

a = ['a', 'b', 'c', 'd']
f = indexed(a)
f(2)


# #### Works with Strings and Dicts

# In[ ]:


s = "abcdef"
indexed("abcdef")(4)
at(3)(s)


# In[ ]:


d = {"a": 2, "b": 3}
indexed(d)("b")
at("b")(d)


# ### Object Accessors

# In[ ]:


@dataclass
class Position:
  "A 2D position."
  x: int = 0
  y: int = 0

p = Position(2, 3)
p


# In[ ]:


def getter(name: str, *default) -> Callable[[Any], Any]:
  return lambda obj: \
    getattr(obj, name, *default)

def object_get(obj: Any) -> Callable[[str], Any]:
  return lambda name, *default: \
    getattr(obj, name, *default)


# In[ ]:


g = getter('x')
g(p)


# In[ ]:


h = object_get(p)
h('x')
h('z', 999)


# In[ ]:


# Positions do not have a `z` attribute:
try:
  h('z')
except AttributeError as x:
  print(repr(x))


# In[ ]:


def setter(name: str) -> Unary:
  return lambda obj, val: setattr(obj, name, val)

def accessor(name: str) -> Callable[[Any, Optional[Any]], Any]:
  def g(obj, *val):
    if val:
      return setattr(obj, name, val[0])
    return getattr(obj, name)
  return g


# In[ ]:


s = setter('x')
s(p, 5)
p


# In[ ]:


a = accessor('x')
a(p)
a(p, 7)
p


# ## Other Adapters

# In[ ]:


def projection(key: Any, *default) -> Callable:
  'Returns a function `f(a)` that returns `a.get(key, default)`.'
  return lambda a: a.get(key, *default)

p = projection("a", 999)
p({"a": 2, "b": 3})
p({})


# # Stateful Closures
#
# Stateful closures are functions that have access to state that is not visible outside the function.

# ### Generators
#
# A generator is an impure function, which may return a different value regardless of its arguments.
# Examples:
# - random number generator
# - reading lines from a file

# In[ ]:


def counter(start: int = 0, increment: int = 1) -> Callable[[], int]:
  "Generator of arithmetic sequences."
  def g() -> int:
    nonlocal start
    result = start
    start += increment
    return result
  return g


# In[ ]:


c = counter(2, 3)
c()
c()
c()


# # Second-Order Functions

#
# Second-Order Functions return other functions.
#
# They often have the form:
#
# ----
#
# ```python
# def f(a: Any, ...):
#   return lambda b: Any, ...: \
#     do_something_with(a, b)
# ```
#
# ----
#
# or
#
# ----
#
# ```python
# def f(a: Any, ...):
#   def g(b: Any, ...):  # `g` has access to `a`
#     return do_something_with(a, b)
#   return g
# ```
# ----

# # Combinators
#
# Combinators:
#
# * are functions that construct closures from other functions.
# * provides a powerful mechanism for reusing logic...
#   without having to anticpate the future.
#
# A combinator `c` may have the form:
#
# ----
# ```python
# def c(f: Callable, ...) -> Callable:    # <-- COMBINATOR
#   def g(b, ...):                        # <-- COMPOSITION
#     return f(do_something_with(a, b))   # <-- APPLICATION and RESULT
#   return g                              # <-- CLOSURE
# ```
# ----
#
# or for brevity:
#
# ----
# ```python
# def c(f: Callable, ...) -> Callable:
#   return lambda b, ...: f(do_something_with(a, b))
# ```
# ----

# ## Stateless Combinators

# ### Tracing Combinator
#
# Wrap a function with tracing information:

# In[ ]:


# Wrap a function that logs input and output.
def trace(f: Callable, name: str | None = None) -> Callable:  # <-- COMBINATOR
    def g(*args, **kwargs):                                   # <-- COMPOSITION
        msg = format_args((name or f.__name__), args, kwargs)
        print(f"{msg} => ...")
        result = f(*args, **kwargs)                           # <-- APPLICATION
        print(f"{msg} => {result!r}")
        return result                                         # <-- RESULT
    return g                                                  # <-- CLOSURE

def format_args(name, args, kwargs):
    return f"{name}(" + ', '.join([repr(x) for x in args] + [f"{k!r}={v!r}" for k, v in kwargs.items()]) + ")"

add = trace(lambda x, y: x + y, "add")
avg = trace(lambda x, y: add(x, y) / 2.0, "avg")
trace(avg)(2, 3)


# # Stateful Combinators

# In[ ]:


def with_counter(f: Callable, i: int = 0) -> Callable:
  'Returns a Callable that applies a counter to f.'
  c = counter(i)                         # <-- STATEFUL CLOSURE AS STATE
  def g(*args, **kwargs):                # <-- COMBINATION
    return f(c(), *args, **kwargs)       # <-- COMPOSITION and RESULT
  return g                               # <-- CLOSURE

def multiply(x, y):
  return x * y

f = with_counter(multiply, 21)
[f(2), f(2), f(3), f(5)]


# ## Indenting Tracer
#
# A prettier version of `trace(f)`.
#
# It tracks indention with a `trace_indent` global variable.

# In[ ]:


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

add = trace(lambda x, y: x + y, "add")
avg = trace(lambda x, y: add(x, y) / 2.0, "avg")
trace(avg)(2, 3)


# # Function Composition

# # Partial Application

#

# # Predicates

# In[ ]:


# Functions with zero or more arguments that return a boolean.
Predicate = Callable[..., bool]

def is_string(x: Any) -> bool:
  'Returns true if `x` is a string.'
  return isinstance(x, str)

is_string("hello")
is_string(3)


# # Predicate Combinators

# In[ ]:


# Functions that take a Predicate and return a new Predicate.
PredicateCombinator = Callable[[Predicate], Predicate]

def not_(f: Predicate) -> Predicate:
  'Returns a function that logically negates the result of the given function.'
  return lambda *args, **kwargs: not f(*args, **kwargs)

h = not_(is_string)
h("hello")
h(3)


# Partial application adds "default" values to a function.

# In[ ]:


def partial(f: Callable, *args, **kwargs) -> Callable:
  'Returns a function that prepends `args` and merges `kwargs`.'
  def g(*args2, **kwargs2):
    return f(*(args + args2), **dict(kwargs, **kwargs2))
  return g

def add_and_multiply(a, b, c):
  return (a + b) * c

add_and_multiply(2, 3, 5)

h = partial(add_and_multiply, 2)
h(3, 5)


# ## Methods are Partially Applied Functions

# In[ ]:


a = 2
b = 3
a + b
a.__add__(b)    # eqv. to `a + b`
h = a.__add__
h
h(7)


# In[ ]:


def partial_right(f: Callable, *args, **kwargs) -> Callable:
  'Returns a function that appends `args` and merges `kwargs`.'
  def g(*args2, **kwargs2):
    return f(*(args2 + args), **(kwargs2 | kwargs))
  return g

def add_and_multiply(a, b, c):
  return (a + b) * c

add_and_multiply(2, 3, 5)

h = partial_right(add_and_multiply, 2)
h(3, 5)


# # Iterative Combinators

# In[ ]:


def fixed_point(f: Unary) -> Unary:
    "Returns a function where: iterate x = f(x) until x no longer changes."
    def g(x):
        while True:
            y = f(x)
            if y == x:
                return y
            x = y
    return g

def f(xy):
  ic(xy)
  x, y = xy
  return (x.replace(y, y[1:]), y[1:])

g = fixed_point(f)
g(("abccabaaxabc", "abc"))


# In[ ]:


def Heron(S: float) -> float:
    def g(x):
        return (x + S / x) / 2.0
    return g
fixed_point(trace(Heron(2.0)))(0.5)


# In[ ]:


math.sqrt(2.0)


# In[ ]:


def Collatz(n):
    if n == 4:
        return n
    ic(n)
    return n // 2 if n % 2 == 0 else n * 3 + 1
fixed_point(Collatz)(88)


# # Manipulating Sequences

# ## Mapping functions over sequences

# In[ ]:


# Note: Python has a built-in `map` -- this is for illustration:
def map(f: Unary, xs: Sequence) -> Sequence:
  'Returns a sequence of `f(x)` for each element `x` in `xs`.'
  acc = []
  for x in xs:
    acc.append(f(x))
  return acc

items = [1, "string", False, True, None]
items
map(identity, items)
map(constantly_7, items)
map(is_string, items)
map(not_(is_string), items)
map(plus_three, [3, 5, 7, 11])


# In[ ]:


# Restore the built-in:
# map = map_


# ## Filtering Sequences with Predicates

# In[ ]:


def filter(f: Unary, xs: Sequence) -> Sequence:
  'Returns a sequence of the elements of `xs` for which `f` returns true.'
  return [x for x in xs if f(x)]

items = [1, "string", False, True, None]
filter(is_string, items)
filter(not_(is_string), items)


# ## Reducing Sequences with Binary Functions

# In[ ]:


# Functions with two arguments that return anything.
Binary = Callable[[Any, Any], Any]

def reduce(f: Binary, init: Any, xs: Sequence) -> Sequence:
  'Returns the result of `init = f(x, init)` for each element `x` in `xs`.'
  for x in xs:
    init = f(init, x)
  return init

def add(x, y):
  return x + y

reduce(add, 2, [3, 5, 7])
a_list_of_strings = ["A", "List", 'Of', 'Strings']
reduce(add, "Here Is ", a_list_of_strings)


# In[ ]:


items = [1, "string", 2, 3, "-and-more", 5]

# Concat all strings:
reduce(add, "", filter(is_string, items))

# Sum of all numbers:
def is_number(x: Any) -> bool:
  return not isinstance(x, bool) and isinstance(x, Number)
reduce(add, 0, filter(is_number, items))

# Sum all non-strings:
reduce(add, 0, filter(not_(is_string), items))


# In[ ]:


def conjoin(a, b) -> Callable[[Any, Any], Tuple[Any, Any]]:
  'Creates a Tuple from two arguments.'
  return (a, b)

items = [3, "a", 5, "b", 7, "c", 11, True]
reduce(conjoin, 2, items)

dict(map(with_counter(conjoin, 21), ["a", "b", "c", "d"]))


# ## Map as a Reduction

# In[ ]:


def map_r(f: Unary, xs: Sequence) -> Sequence:
  def acc(seq, x):
    return seq + [f(x)]
  return reduce(acc, [], xs)

map(plus_three, [3, 5, 7, 11])
map_r(plus_three, [3, 5, 7, 11])


# ## Filter as a Reduction

# In[ ]:


def filter_r(f: Unary, xs: Sequence) -> Sequence:
  def acc(seq, x):
    return seq + [x] if f(x) else seq
  return reduce(acc, [], xs)

items
filter(is_string, items)
filter_r(is_string, items)


# ## Mapcat (aka Flat-Map)

# In[ ]:


ConcatableUnary = Callable[[Any], Sequence]

def mapcat(f: ConcatableUnary, xs: Sequence):
  'Concatenate the results of `map(f, xs)`.'
  return reduce(add, [], map(f, xs))

def duplicate(n, x):
  return [x] * n

duplicate_each_3_times = partial(mapcat, partial(duplicate, 3))
duplicate_each_3_times([".", "*"])
duplicate_each_3_times(range(4, 7))


# ## Manipulating Arguments

# In[ ]:


def reverse_args(f: Callable) -> Callable:
  def g(*args, **kwargs):
    return f(*reversed(args), **kwargs)
  return g

def divide(x, y):
  return x / y

divide(2, 3)
reverse_args(divide)(2, 3)

reduce(reverse_args(add), " reversed ", a_list_of_strings)
reduce(reverse_args(conjoin), 2, [3, 5, 7])


# In[ ]:


def compose(*callables) -> Variadic:
  'Returns the composition one or more functions, in reverse order.'
  'For example, `compose(g, f)(x, y)` is equivalent to `g(f(x, y))`.'
  f: Callable = callables[-1]
  gs: Sequence[Unary] = tuple(reversed(callables[:-1]))
  def h(*args, **kwargs):
    result = f(*args, **kwargs)
    for g in gs:
      result = g(result)
    return result
  return h

def multiply_by_3(x):
  return x * 3

plus_three(multiply_by_3(5))

h = compose(plus_three, multiply_by_3)
h(5)


# In[ ]:


def juxt(*fs):
    "Returns a function that applies each f in fs to its arguments."
    def g(*args, **kwargs):
        return map(lambda f: f(*args, **kwargs), fs)
    return g

def negative(x):
    return - x

def repeat(n, x):
    return [x] * n

map(juxt(identity, negative, partial(repeat, 3)), [2, 3, 5, 7])


# # Interlude

# In[ ]:


def modulo(modulus: int) -> Callable[[int], int]:
  return lambda x: x % modulus

mod_3 = modulo(3)
map(mod_3, range(10))


# In[ ]:


h = compose(indexed(a_list_of_strings), mod_3)
a_list_of_strings
map(h, range(10))


# ### Arity Reduction

# In[ ]:


def unary(f: Variadic) -> Unary:
  return lambda *args, **kwargs: f((args, kwargs))

h = unary(identity)
h()
h(1)
h(1, 2)
h(a=1, b=2)


# # Developer Affordance

# ## Error Handlers

# In[ ]:


def except_(f: Variadic, ex_class, error: Unary) -> Callable:
  def g(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except ex_class as exc:
      return error((exc, args, kwargs))
  return g

h = except_(plus_three, TypeError, compose(partial(logging.error, 'plus_three: %s'), repr))
h(2)
h('Nope')


# # Web Application Architecture
#
# Application middleware combinators inspired Python WSGI and Ruby Rack.
#
# - An "App" is anything callable with a single dict argument.
# - It receives a "Request"
#   - typically a Dict of input: headers, body and customary values passed along an "application stack".
# - It returns an HTTP "Response": Tuple of:
#   - numeric HTTP status code
#   - dict of HTTP headers
#   - body -- a sequence of response body chunks
# - applications and middleware follow the same protocol.
# - Combinators create new Apps by wrapping others.
#

# In[ ]:


# Types for a Web Application Stack:
Status = int
Headers = Dict[str, Any]
Body = Iterable[bytes | str]
Req = Dict[str, Any]
Res = Tuple[Status, Headers, Body]
App = Callable[[Req], Res]


# ## Simple Applications

# In[ ]:


def hello_world_app(req: Req) -> Res:
  return 200, {}, ["Hello, World!\n"]
app = hello_world_app
app({})


# ### Do Something Useful

# In[ ]:


def something_useful_app(req: Req) -> Res:
  x, y = req['req.data']
  return 200, {}, (x * y,)

app = something_useful_app
app({'req.data': [2, 5]})


# In[ ]:


app = something_useful_app
app({'req.data': ["ab", 3]})


# ## Application Combinators

# Input combinators follow this pattern:

# In[ ]:


def compose_input_handler(app: App) -> App:
  def input_handler(req: Req) -> Res:
    # do something with req...
    return app(req)
  return input_handler


# Output combinators follow this pattern:

# In[ ]:


def compose_output_handler(app: App) -> App:
  def output_handler(req: Req) -> Res:
    status, headers, body = response = app(req)  # <<<
    # do something with response...
    return status, headers, body
  return output_handler


# ## App Stack Tracing

# In[ ]:


app = something_useful_app
app = trace(app)
app({'req.data': [5, 7]})


# In[ ]:


# Composition Naming
def compname(g, name, *args):
    args = [a.__qualname__ if callable(a) else repr(a) for a in args]
    g.__qualname__ = f"{g}({','.join(args)})"
    return g


# In[ ]:


def app_comp(app: App, *stack) -> App:
    "Compose application stack."
    app = trace(app)
    for middleware in stack:
        app = trace(compname(middleware(app), middleware.__qualname__, app))
    return app


# ## Exception Handling

# In[ ]:


def capture_exception(app: App, cls=Exception, status=500) -> App:
    def capturing_exception(req: Req) -> Res:
        try:
            return app(req)
        except cls as exc:
            return status, {"Content-Type": "text/plain"}, (repr(exc),)
    return capturing_exception


# In[ ]:


app = something_useful_app
app = capture_exception(app)
app({'req.data': [{"a": 1}, 7]})


# ## Reading Inputs, Writing Outputs

# In[ ]:


Content = str
Data = Any

def read_input(app: App) -> App:
    "Reads req.stream"
    def reader(req: Req) -> Res:
        # TODO: check inbound Content-Length
        req["req.content"] = req["req.stream"].read()
        req["Content-Length"] = len(req["req.content"])
        return app(req)
    return reader


# ## Decoding Inputs, Encoding Outputs

# In[ ]:


Encoder = Callable[[Data], Content]
Decoder = Callable[[Content], Data]

def decode_content(app: App, decoder: Decoder, content_types=None, strict=False) -> App:
    """
    Decodes body with decoder(input.content) for content_types.
    If strict and Content-Type is not expected, return 400.
    """

    def decoding_content(req: Req) -> Res:
        req["req.data"] = decoder(req["req.content"])
        content_type = req.get("Content-Type")
        if strict and content_types and content_type not in content_types:
            msg = f"Unexpected Content-Type {content_type!r} : expected: {content_types!r} : "
            return 400, {"Content-Type": 'text/plain'}, (msg,)
        return app(req)
    return decoding_content


def encode_content(app: App, encoder: Encoder, content_type="text/plain") -> App:
    "Encodes body with encoder.  Sets Content-Type."
    def encoding_content(req: Req) -> Res:
        status, headers, body = app(req)
        content = "".join(map(encoder, body))
        headers |= {
            "Content-Type": content_type,
            "Content-Length": len(content),
        }
        return status, headers, [content]
    return encoding_content


# ## Decode JSON, Encode JSON

# In[ ]:


import json

def decode_json(app: App, **kwargs) -> App:
    "Decodes JSON content."
    def decoding_json(data: Data) -> Any:
        return json.loads(data, **kwargs)
    return decode_content(app, decoding_json, content_types={'application/json', 'text/plain'}, strict=True)


def encode_json(app: App, **kwargs) -> App:
    "Encodes data as JSON."
    def encoding_json(data: Data) -> Content:
        return json.dumps(data, **kwargs) + "\n"
    return encode_content(app, encoding_json, content_type='application/json')


# ## HTTP Protocol

# In[ ]:


def http_request(app: App) -> App:
    def http_req(req):
        req_io = req["req.stream"]
        request_method, path_info, server_protocol = req_io.readline().split(" ", 3)
        req = {}
        while line := req_io.readline().rstrip():
            k, v = line.strip().split(":", 2)
            req[k] = v.strip()
        req.update({
            "REQUEST_METHOD": request_method,
            "PATH_INFO": path_info,
            "SERVER_PROTOCOL": server_protocol,
            "req.stream": req_io,
            # "output.stream": res_io,
        })
        return app(req)
    return http_req

def http_response(app: App) -> App:
    def http_res(req):
        status, headers, body = app(req)
        res_io = req['res.stream']
        res_io.write(f"HTTP/1.1 {status} ...\n")
        for k, v in headers.items():
            res_io.write(f"{k}: {v}\n")
        res_io.write("\n")
        for chunk in body:
            if callable(chunk):
                chunk(res_io)
            res_io.write(chunk)
    return http_res

req_str = """\
POST / HTTP/1.1
Host: hello.world.com
Accept: */*
Content-Type: text/plain

Are you there?
"""
req_io = StringIO(req_str)
res_io = sys.stdout # StringIO()
app = app_comp(hello_world_app, http_request, http_response)
req = {"req.stream": req_io, "res.stream": res_io}
app(req)


# ## Simple App Handles JSON!

# In[ ]:


app = app_comp(something_useful_app, decode_json, encode_json, read_input, capture_exception, http_request, http_response)
req_str = """\
POST / HTTP/1.1
Host: hello.world.com
Accept: */*
Content-Type: application/json

[2, 3]
"""
req_io = StringIO(req_str)
res_io = sys.stdout # StringIO()
req = {"req.stream": req_io, "res.stream": res_io}
app(req)


# # Logical Combinators

# ## Predicators

# In[ ]:


def re_pred(pat: str, re_func: Callable = re.search) -> Predicate:
  'Returns a predicate that matches a regular expression.'
  rx = re.compile(pat)
  return lambda x: re_func(rx, str(x)) is not None

re_pred("ab")("abc")
re_pred("ab")("nope")


# In[ ]:


def default(f: Variadic, g: Variadic) -> Variadic:
  def h(*args, **kwargs):
    if (result := f(*args, **kwargs)) is not None:
      return result
    return g(*args, **kwargs)
  return h


# asdf

# ## Logical Predicate Composers

# In[ ]:


def and_(f: Variadic, g: Variadic) -> Variadic:
  'Returns a function `h(x, ...)` that returns `f(x, ...) and g(x, ...).'
  return lambda *args, **kwargs: f(*args, **kwargs) and g(*args, **kwargs)

def or_(f: Variadic, g: Variadic) -> Variadic:
  'Returns a function `h(x, ...)` that returns `f(x, ...) or g(x, ...).'
  return lambda *args, **kwargs: f(*args, **kwargs) or g(*args, **kwargs)

def is_int(x):
  return isinstance(x, int)

def is_string(x):
  return isinstance(x, str)

is_word = re_pred(r'^[a-z]+$')

# If x is an int, add three:
h = and_(is_int, plus_three)
# If x is a string, is it a word?:
g = and_(and_(is_string, is_word), len)
# One or the other:
func = or_(h, g)
items = ["hello", "not-a-word", 2, 3.5, None]
map(juxt(identity, func), items)


# In[ ]:


Procedure = Callable[[], Any]

def if_(f: Variadic, g: Unary, h: Unary) -> Variadic:
  def i(*args, **kwargs):
    if (result := f(*args, **kwargs)):
      return g()
    return h()
  return i


# # Interpreters

# ## Operator Predicates

# In[ ]:


def binary_op(op: str) -> Optional[Callable[[Any, Any], Any]]:
  'Returns a function for a binary operator by name.'
  return BINARY_OPS.get(op)

BINARY_OPS = {
  '+': lambda a, b: a + b,
  '-': lambda a, b: a - b,
  '*': lambda a, b: a * b,
  '/': lambda a, b: a / b,
  '==': lambda a, b: a == b,
  '!=': lambda a, b: a != b,
  '<':  lambda a, b: a < b,
  '>':  lambda a, b: a > b,
  '<=': lambda a, b: a <= b,
  '>=': lambda a, b: a >= b,
  'and': lambda a, b: a and b,
  'or': lambda a, b: a or b,
}
for n, f in BINARY_OPS.items():
  f.__name__ = f"binary_op({n!r})"

binary_op('==') (2, 2)
binary_op('!=') (2, 2)


# In[ ]:


# Create a table where `x OP y` is true:
[
  f'{x} {op} {y}'
  for op in ['<', '==', '>']
  for x in (2, 3, 5)
  for y in (2, 3, 5)
  if binary_op(op)(x, y)
]


# In[ ]:


def stacky(program, trace=identity):
    'A stack-oriented expression evaluator.'
    def eval(stack, item):
        if isinstance(item, int):
            return stack + [item]
        else:
            return stack[:-2] + [item(stack[-2], stack[-1])]
    def parse(word):
        if re.match(r'-?\d+', word):
            return int(word)
        return binary_op(word)
    return reduce(trace(eval), [], map(trace(parse), program.split(" ")))

stacky("2 3 5 + *")
stacky("33 2 3 + 5 * >")
stacky("2 3 *", trace)


# In[ ]:


def op_pred(op: str, b: Any) -> Predicate | None:
  'Returns a predicate function given an operator name and a constant.'
  if pred := binary_op(op):
    return lambda a: pred(a, b)
  if op == "not":
    return lambda a: not a
  if op == "~=":
    return re_pred(b)
  if op == "~!":
    return not_(re_pred(b))
  return None


# In[ ]:


h = op_pred(">", 3)
h(2)
h(5)


# In[ ]:


g = op_pred("~=", 'ab+c')
g('')
g('ab')
g('abbbcc')


# ## Sequencing

# In[ ]:


def progn(*fs: Sequence[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = None
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g


# In[ ]:


def prog1(f0: Callable, *fs: Sequence[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = f0(*args, **kwargs)
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g


# In[ ]:


def reverse_apply(x: Any) -> Callable:
  return lambda f, *args, **kwargs: f(x, *args, **kwargs)

reverse_apply(1) (plus_three)


# In[ ]:





# ## Parser Combinators

# In[ ]:


# Parser input: a sequence of lexemes:
Input = Sequence[Any]

# A parsed value and remaining input:
Parsed = Tuple[Any, Input]

# A parser matches the input sequence and produces a result or nothing:
Parser = Callable[[Input], Parsed | None]


# In[ ]:


def show_match(p: Parser) -> Variadic:
  def g(input: Input):
    return (p(input) or False, '<=', input)
  return g


# In[ ]:


first = at(0)
def rest(x: Input) -> Input:
  return x[1:]

def equals(x) -> Parser:
  'Returns a parser that matches `x`.'
  def g(input: input):
    y = first(input)
    logging.debug("equals(%s, %s)", repr(x), repr(y))
    if x == y:
      return y, rest(input)
  return g

h = equals('a')
h(['a'])
h(['b', 2])


# In[ ]:


def which(p: Predicate) -> Parser:
  'Returns a parser for the next lexeme when `p(lexeme)` is true.'
  def g(input: Input):
    if p(first(input)):
      return (first(input), rest(input))
  return g

g = which(is_string)
g(['a'])
g([2])
g(['a', 'b'])

def alternation(*ps) -> Parser:
  def g(input):
    for p in ps:
      if (result := p(input)):
        return result
  return g

g = alternation(which(is_string), which(is_number))
g(['a'])
g([2])
g([False])


# ## Sequence Parsers

# In[ ]:


ParsedSequence = Tuple[Sequence, Input]
SequenceParser = Callable[[Input], ParsedSequence | None]

def one(p: Parser) -> SequenceParser:
  'Returns a parser for one lexeme.'
  def g(input: Input):
    if input and (result := p(input)):
      parsed, input = result
      return [parsed], input
  return g

g = one(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])


# In[ ]:


def zero_or_more(p: Parser) -> SequenceParser:
  'Returns a parser for zero or more lexemes.'
  def g(input: Input):
    acc = []
    while input and (result := p(input)):
      parsed, input = result
      acc.append(parsed)
    return acc, input
  return g

g = zero_or_more(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


def one_or_more(p: Parser) -> SequenceParser:
  'Returns a parser for one or more lexemes as a sequence.'
  p = zero_or_more(p)
  def g(input: Input):
    if (result := p(input)) and len(result[0]) >= 1:
      return result
  return g


# In[ ]:


g = one_or_more(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


def sequence_of(*parsers) -> SequenceParser:
  'Returns a parser for parsers of a sequence.'
  def g(input: Input):
    acc = []
    for p in parsers:
      if result := p(input):
        parsed, input = result
        acc.extend(parsed)
      else:
        return None
    return acc, input
  return g

g = sequence_of(one(which(is_string)), one(which(is_string)))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


g = sequence_of(one_or_more(which(is_number)))
g([])
g(['a'])
g([2])
g([2, 3])
g([2, 3, False])


# In[ ]:


g = sequence_of(one(which(is_string)), one_or_more(which(is_number)))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 2])
g(['a', 2, 3])
g(['a', 2, 'b', 3])
g(['a', 2, 3, False])
g(['a', 2, 3, False, 'more'])


# ## Parser Grammar

# In[ ]:


def take_while(f: Unary) -> Unary:
  def g(seq):
    acc = []
    while seq and (x := f(seq[0])):
      acc.append(x)
    return acc
  return g

def action(p: Parser, f: Callable[[Any], Any]) -> Parser:
  'Returns a parser that calls `f` with parsed value.'
  def g(seq):
    if result := p(seq):
      return a(result[0]), result[1]
  return g

env = {}
def a(v):
  # nonlocal x
  env['x'] = v
  return v
f = action(which(is_string), a)
f(["abc"])
env


# ## Lexical Scanning

# In[ ]:


def eat(rx: str):
  p = re.compile(rx)
  return lambda s: re.sub(p, '', s)

def lexeme(pat: str, post = at(0)):
  post = post or (lambda m: m[0])
  rx = re.compile(pat)
  ws = eat(r'^\s+')
  def g(input):
    input = ws(input)
    if input and (m := re.match(rx, input)):
      return post(m), input[len(m[0]):]
  return g


# In[ ]:


def grammar_parser():
  env = {}
  def _(id):
    return lambda *args: env[id](*args)

  def action(p: Parser, action: Unary) -> Parser:
    def g(input: Input):
      if result := p(input):
        value = action(result[0])
        return value, result[1]
    return g

  def cache(p: Parser) -> Parser:
    '''
    Cache the result of p(input).
    This improves performance when a definition is
    parsed multiple times.
    '''
    d = {}
    def g(input):
      if v := d.get(id(input)):
        # logging.debug('cached : %s => %s', repr(input), repr(v[0]))
        return v[0]
      v = p(input)
      d[id(input)] = (v,)
      return v
    return g

  def definition(id, p, act=None):
    # p = trace(p, id)
    # p = cache(p)
    a = None
    if act is True:
      a = lambda x: (id, x)
    elif isinstance(act, str):
      a = lambda x: (act, x)
    elif act:
      a = act
    if a:
      p = action(p, a)
    p = cache(p)
    env[id] = p

  definition('string',        lexeme(r'^"(\\"|\\?[^"]+)*"',
                                lambda m: ('string', eval(m[0]))))
  definition('regex',         lexeme(r'^/((\\/|(\\?[^/]+))*)/',
                                lambda m: ('regex', re.compile(m[1]))))
  definition('name',          lexeme(r'^[a-zA-Z][a-zA-Z0-9_]*'))
  definition('terminal',      alternation(_("string"), _('regex')))
  definition('non_terminal',  _('name'),
                                lambda x: ('reference', x))
  definition('action',        lexeme(r'^@\{(.+?)\}@',
                                lambda m: ('action', m[1].strip())))
  definition('basic_match',   alternation(_('non_terminal'), _('terminal')))
  definition('bound_match',   sequence_of(one(_('basic_match')), one(lexeme(r'^:')), one(_('name'))),
                                lambda x: ('bound_match', x[0], x[2]))
  definition('match',         alternation(_('bound_match'), _('basic_match')))
  definition('matches',       one_or_more(_('match')))
  definition('matches_with_action', sequence_of(_('matches'), one(_('action'))))
  definition('pattern',       alternation(_('matches_with_action'), _('matches')))
  definition('sequence',      sequence_of(_('pattern')), lambda x: ('sequence', x))
  definition('alternation',   sequence_of(one(_('sequence')), one(lexeme(r'\|')), one(_('production'))),
                                lambda x: ('alternation', x[0], x[2]))
  definition('production',    alternation(_('alternation'), _('sequence')))
  definition('definition',    sequence_of(one(_('name')), one(lexeme(r"=")), one(_('production')), one(lexeme(r';'))),
                                lambda x: ('definition',  x[0], x[2]))
  definition('grammar',       sequence_of(one_or_more(_('definition'))), 'grammar')

  def g(input, start=None):
    return _(start or 'grammar')(input)
  return g


# In[ ]:


grammar_tests = [
  # [r'"asdf"'], # , 'pattern'],
  # [r'  a = "asdf";'],
  # [r'  a = b c;'],
  # [r'a =b c|d;'],
  # [r'a = b c | d | e f;'],
  # [r'a = "foo";'],
  [r'b = /^foo/:c @{ do_this(c) }@;'],
  # [r'a = b : x c : y @{ do_this(x, y) }@ ;'],
  [r'''
expr = mult | add | const;
mult = expr "*" expr;
add = expr "+" expr;
const = /^[-+]?\d+/;
  ''']
]

gram = grammar_parser()

for grammar_test in grammar_tests:
  logging.debug("============================================\n")
  ic(grammar_test)
  result = gram(*grammar_test)
  ic(result)


# ## Grammar Compiler

# In[ ]:


def compile_grammar(gram, parser_name):
  gensym_i = 0
  def gensym(name):
    nonlocal gensym_i
    gensym_i += 1
    return f"__{name}__{gensym_i}"

  ref_cache = {}
  def ref(name):
    nonlocal ref_cache
    if x := ref_cache.get(name):
      return x
    x = ref_cache[name] = gensym(name)
    return x

  input = gensym('input')
  result = gensym('result')
  newlines = "\n\n"
  depth = 0

  stack = []
  def push():
    stack.append((input, result))

  def pop():
    input, result = stack.pop()

  def indent(s, chars):
    prefix = f"\n{' ' * chars}"
    return prefix.join(map(lambda s: f"{prefix}{x}", s.split("\n")))

  def advance(value, remaining = f"{result}[1]"):
    return f"""
    {result} = ({value}, {remaining})
    {input} = {result}[1]
  """

  def grammar(definitions):
    start_name = definitions[0][1]
    return f"""
def {parser_name}({input}):
{newlines.join(map(compile, definitions))}
  return {ref(start_name)}({input})
"""

  def definition(name, production):
    return f"""
  def {ref(name)}({input}):
    {result} = None
{compile(production)}
    return {result}
"""

  def alternation(*exprs):
    code = ""
    input_save = gensym('input')
    code += f"""
    {input_save} = {input}
"""
    for expr in exprs:
      code += compile(expr)
      push()
      result = gensym('result')
      code += f"""
{compile(expr)}
    if {result}:
      return {result}
    {input} = {input_save}
"""
      pop()
    code += f"""
      return {result}
"""
    return code

  def sequence(exprs):
    sequence = gensym('sequence')
    code = ""
    code += f"""
    {sequence} = []
"""
    for expr in exprs:
      code += f"""
{compile(expr)}
    if not {result}:
      return None
    {sequence}.append({result}[0])
{advance(sequence)}
"""
    return code

  def reference(name):
    return f"""
    {result} = {ref(name)}({input})
"""

  def patterns(exprs):
    return "\n".join(map(compile, exprs))

  def bound_match(expr, name):
    return f"""
{compile(expr)}
    {name} = {result} and {result}[0]
"""

  def matches_with_action(expr):
    ic(expr)
    return f"""
{compile(expr)}
    if {result}:
      return {indent(action, 6)}, {input}
"""

  def string(s):
    const = repr(s)
    check = f"({input}[0:{len(s)}] == {const})"
    return f"""
    if not {check}:
      return None
{advance(const, f"{input}[:{len(s)}]")}
"""

  def integer(expr):
    match = gensym('match')
    return f"""
    if not ({match} := re.search(r'^([-+]?\\d+)', {input})):
      return None
{advance(f"int({match}[1])", f"{input}[:len({match}[1])]")}
"""

  def regex(expr):
    match = gensym('match')
    return f"""
    if not ({match} := {expr!r}.search({input}):
      return None
{advance(f"{match}[1]", f"{input}[0:len({match}[1])]")}
"""

  def action(code):
    # ic(("action", code))
    return f"""
    {result} = ({code})
{advance(result, input)}
"""

  funcs = locals()
  def compile(expr):

    # ic(("compile", expr))
    nonlocal depth
    depth += 1
    indent = '  ' * depth
    result = funcs[expr[0]](*expr[1:])
    depth -= 1
    indent = '  ' * depth
    result = f"{indent}### {expr!r}\n{result}"
    result = "\n".join([line for line in result.splitlines() if line])
    return result
    return f"""
{indent}####################################
{indent}# {repr(expr)} (((
{result}
{indent}# {repr(expr)} )))
{indent}####################################
"""

  return compile(gram)

gram = grammar_parser()
for i, grammar_test in enumerate(grammar_tests):
  print("")
  print("### ============================================")
  print(f"''' {grammar_test[0]} '''")
  # ic(grammar_test)
  grammar_parsed = gram(*grammar_test)[0]
  print(f"''' {grammar_parsed!r} '''")
  # ic(grammar_parsed)
  print(compile_grammar(grammar_parsed, f"parser_{i}"))
  print("### ============================================")


# ----
# # The End
# ----
