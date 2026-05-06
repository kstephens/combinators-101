# %%capture import_io
from c101.helpers import *
from c101.combinators_101 import *
import operator as op
import inspect
from typing import Any, Optional, Union, List, Tuple, Dict, Iterable, Mapping, Callable, Type, Literal, IO, NoReturn, Self

"""
# Second-Order Functions

Second-Order Functions return new functions (closures) using the arguments given to them.

Often have the form:

```python
def f(a, ...):                       # <== SECOND-ORDER FUNCTION
  # g() has access to a:
  def g(b, ...):                     # <== FIRST-ORDER FUNCTION has access to `a`
    return something(a, b)   # <== Uses `a` and `b`
  return g
```
"""

"""
----
"""

"""
# Combinators

Combinators:

* are functions that construct closures from other functions.
* provide a powerful mechanism for reusing logic.
* hide information.
* create explicit interfaces with ease.

A combinator `c` may have the form:

```python
def c(f: Callable, ...) -> Callable:    # <-- COMBINATOR
  def g(a, b, ...):                     # <-- COMPOSITION
    return f(something(a, b))   # <-- APPLICATION and RESULT
  return g                              # <-- CLOSURE
```

or for brevity:

```python
def c(f: Callable, ...) -> Callable:
  return lambda a, b, ...: f(something(a, b))
```

"""

"""
Combinators presented here may return functions that will receive `*args*` and `**kwargs`.

This is a common pattern:
"""

def print_args(f: Callable) -> Callable:    # <-- COMBINATOR
  "Return a function that prints *args and **kwargs before calling f(...)."
  def g(*args, **kwargs):                     # <-- COMPOSITION
    print(repr((args, kwargs)))                  # <-- NEW BEHAVIOR
    return f(*args, **kwargs)                    # <-- APPLICATION and RESULT
  return g                                       # <-- CLOSURE

def f(x, y):
  return x + y

print_args_then_call_f = print_args(f)
print_args_then_call_f(2, 3)

"""
----
"""

"""
# Stateless Combinators
"""

"""
## Function Arity Helper
"""

"""
In some languages functions defintions can have the same name with different parameter lists.

```C++
void print(int x);
void print(int x, int y);
print(1)
print(2)
```

Python does not have this feature... but here's a combinator for it...
"""

def arity(*funcs):
  "Returns a function that dispatches based on the arity of the functions given and the arguments from the caller."
  funcs = tuple([(f, len(inspect.signature(f).parameters)) for f in funcs])
  def g(*args, **kwargs):
    for f, n in funcs:
      if len(args) == n:
        return f(*args, **kwargs)
    raise RuntimeError(f"nargs {len(args)!r} : {funcs!r}")
  return g

neg_1_or_sub_2 = arity(op.neg, op.sub)
neg_1_or_sub_2(2)      ;  op.neg(2)
neg_1_or_sub_2(11, 5)  ;  op.sub(11, 5)

"""
## Tracing Combinator

Wrap a function with tracing information:
"""

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
f = trace(lambda x, y: add(x, y) / y, "f")
f(2, 3)
try:
    f(2, 0)
except Exception as e:
    print(e)

"""
----
"""

"""
# Stateful Combinators

Stateful combinators create functions that have side-effects.
Meaning, they might behave different, because they have a "secret" that they change.
"""

def with_counter(f: Callable, i: int = 0) -> Callable:
  'Returns a Callable that applies a counter to f.'
  c = counter(i)                         # <-- LOCAL STATE
  def g(*args, **kwargs):                # <-- COMBINATION
    return f(c(), *args, **kwargs)       # <-- COMPOSITION and RESULT
  return g                               # <-- CLOSURE

def multiply(x, y):
  return x * y

f = with_counter(multiply, 21)
[f(2), f(2), f(3), f(5)]

"""
## Indenting Tracer

A prettier version of `trace(f)`.

It tracks indention with a `trace_indent` global variable.
"""

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
        print(f"{color_g}{ind}\u2570\u2574{color_} {color_b}{result!r}{color_}")
        return result                                        # <--- RESULT
    return g                                                 # <--- CLOSURE

add = trace(lambda x, y: x + y, "add")
f = trace(lambda x, y: add(x, y) / y, "f")
f(2, 3)

try:
    f(2, 0)
except Exception as e:
    print(e)

"""
----
"""

"""
# Predicates
"""

# Functions with zero or more arguments that return a boolean.
Predicate = Callable[..., bool]

def is_string(x: Any) -> bool:
  'Returns true if `x` is a string.'
  return isinstance(x, str)

is_string("hello")
is_string(3)

"""
----
"""

"""
# Function Composition

Functions are combinined into new functions.
"""

"""
## Predicate Combinators
"""

# Functions that take a Predicate and return a new Predicate.
PredicateCombinator = Callable[[Predicate], Predicate]

def not_(f: Predicate) -> Predicate:
  'Returns a function that logically negates the result of the given function.'
  return lambda *args, **kwargs: not f(*args, **kwargs)

g = not_(is_string)
g("hello")
g(3)

"""
# Partial Application

Partial application adds "default" arguments.
"""

"""
## Methods are Partially Applied Functions

The first "hidden" argument of a method is the object.

The method is "bound" to the object.

In other words, a method is a function partially applied to its object.
"""

a, b = 2, 3
a + b
a.__add__(b)    # eqv. to `a + b`
f = a.__add__
f               # h is the partial application of (2).__add__
f(b)

"""
## Generic Partial Application
"""

def partial(f: Callable, *args, **kwargs) -> Callable:
  'Returns a function that prepends `args` and merges `kwargs`.'
  def g(*args2, **kwargs2):
    return f(*(args + args2), **(kwargs | kwargs2))
  return g

def add_and_multiply(a, b, c):
  return (a + b) * c

add_and_multiply(2, 3, 5)

g = partial(add_and_multiply, 2)
g(3, 5)

def partial_right(f: Callable, *args, **kwargs) -> Callable:
  'Returns a function that appends `args` and merges `kwargs`.'
  def g(*args2, **kwargs2):
    return f(*(args2 + args), **(kwargs2 | kwargs))
  return g

g = partial_right(add_and_multiply, 2)
g(3, 5)

"""
# Composition
"""

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

h = compose(str)
h("abc")
h(5)

h = compose(repr, str)
h("abc")
h(5)

len(repr(str("abc")))
h = compose(len, repr, str)
h("abc")

def multiply_by_3(x):
  return x * 3

h = compose(plus_three, multiply_by_3)
h(5)

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

"""
# Iterative Combinators
"""

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
  x, y = xy
  return (x.replace(y, y[1:]), y[1:])

g = fixed_point(trace(f))
g(("abccabaaxabc", "abc"))

def Heron(S: float) -> float:
    def g(x):
        return (x + S / x) / 2.0
    return g

def sqrt(S: float) -> float:
    S = float(S)
    return fixed_point(trace(Heron(S)))(S / 2)

sqrt(50.0)
math.sqrt(50.0)

def Collatz(n):
    if n == 1:
        return n
    return n // 2 if n % 2 == 0 else n * 3 + 1
fixed_point(trace(Collatz))(53)

"""
# Manipulating Sequences
"""

"""
## Mapping functions over sequences
"""

# Note: Python has a built-in `map` -- this is for illustration:
def map(f: Unary, xs: Iterable) -> Iterable:
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

# Restore the built-in:
# map = map_

"""
## Filtering Sequences with Predicates
"""

def filter(f: Unary, xs: Iterable) -> Iterable:
  'Returns a sequence of the elements of `xs` for which `f` returns true.'
  return [x for x in xs if f(x)]

items = [1, "string", False, True, None]
filter(is_string, items)
filter(not_(is_string), items)

"""
## Reducing Sequences with Binary Functions
"""

def reduce(f: Binary, xs: Iterable, init: Any) -> Any:
  'Returns the result of `init = f(x, init)` for each element `x` in `xs`.'
  for x in xs:
    init = f(init, x)
  return init

def add(x, y):
  return x + y

reduce(add, [3, 5, 7], 2)
a_list_of_strings = ["A", "List", 'Of', 'Strings']
reduce(add, a_list_of_strings, "Here Is ")

items = [1, "string", 2, 3, "-and-more", 5]

# Concat all strings:
reduce(add, filter(is_string, items), "")

# Sum of all numbers:
def is_number(x: Any) -> bool:
  return not isinstance(x, bool) and isinstance(x, Number)
reduce(add, filter(is_number, items), 0)

# Sum all non-strings:
reduce(add, filter(not_(is_string), items), 0)

def conjoin(a, b) -> Callable[[Any, Any], Tuple[Any, Any]]:
  'Creates a Tuple from two arguments.'
  return (a, b)

items = [3, "a", 5, "b", 7, "c", 11, True]
reduce(conjoin, items, 2)

dict(map(with_counter(conjoin, 21), ["a", "b", "c", "d"]))

"""
## Map as a Reduction
"""

def map_r(f: Unary, xs: Iterable) -> Iterable:
  def acc(seq, x):
    return seq + [f(x)]
  return reduce(acc, xs, [])

map(plus_three, [3, 5, 7, 11])
map_r(plus_three, [3, 5, 7, 11])

"""
## Filter as a Reduction
"""

def filter_r(f: Unary, xs: Iterable) -> Iterable:
  def acc(seq, x):
    return seq + [x] if f(x) else seq
  return reduce(acc, xs, [])

items
filter(is_string, items)
filter_r(is_string, items)

"""
## Mapcat (aka Flat-Map)
"""

ConcatableUnary = Callable[[Any], Iterable]

def mapcat(f: ConcatableUnary, xs: Iterable):
  'Concatenate the results of `map(f, xs)`.'
  return reduce(add, map(f, xs), [])

def duplicate(n, x):
  return [x] * n

duplicate_each_3_times = partial(mapcat, partial(duplicate, 3))
duplicate_each_3_times([".", "*"])
duplicate_each_3_times(range(4, 7))

"""
## Manipulating Arguments
"""

def reverse_args(f: Callable) -> Callable:
  def g(*args, **kwargs):
    return f(*reversed(args), **kwargs)
  return g

def divide(x, y):
  return x / y

divide(2, 3)
reverse_args(divide)(2, 3)

reduce(reverse_args(add), a_list_of_strings, " reversed ")
reduce(reverse_args(conjoin), [3, 5, 7], 2)

"""
# Interlude
"""

def modulo(modulus: int) -> Callable[[int], int]:
  return lambda x: x % modulus

mod_3 = modulo(3)
map(mod_3, range(10))

h = compose(indexed(a_list_of_strings), mod_3)
a_list_of_strings
map(h, range(10))

"""
### Arity Reduction
"""

def unary(f: Variadic) -> Unary:
  return lambda *args, **kwargs: f((args, kwargs))

h = unary(identity)
h()
h(1)
h(1, 2)
h(a=1, b=2)

"""
# Developer Affordance
"""

"""
## Error Handlers
"""

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

"""
# Logical Combinators
"""

"""
## Predicators
"""

def re_pred(pat: str, re_func: Callable = re.search) -> Predicate:
  'Returns a predicate that matches a regular expression.'
  rx = re.compile(pat)
  return lambda x: re_func(rx, str(x)) is not None

re_pred("ab")("abc")
re_pred("ab")("nope")

def default(f: Variadic, g: Variadic) -> Variadic:
  def h(*args, **kwargs):
    if (result := f(*args, **kwargs)) is not None:
      return result
    return g(*args, **kwargs)
  return h

"""
asdf
"""

"""
## Logical Predicate Composers
"""

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


Procedure = Callable[[], Any]

def if_(f: Variadic, g: Unary, h: Unary) -> Variadic:
  def i(*args, **kwargs):
    if (result := f(*args, **kwargs)):
      return g()
    return h()
  return i

"""
----
"""

"""
## Sequencing
"""

def progn(*fs: Iterable[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = None
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g

def prog1(f0: Callable, *fs: Iterable[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = f0(*args, **kwargs)
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g

def reverse_apply(x: Any) -> Callable:
  return lambda f, *args, **kwargs: f(x, *args, **kwargs)

reverse_apply(1) (plus_three)

"""
----
# The End
----
"""
