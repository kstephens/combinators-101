"""
# (Imports)
"""

from c101.helpers import *
import operator as op
import inspect
from typing import Any, Optional, Union, List, Tuple, Dict, Iterable, Mapping, Callable, Type, Literal, IO, NoReturn, Self

"""
# Combinators-101

This workshop is about building functions with functions.

* functions as values.
* function types.
* information hiding with functions.
* functions that create functions.
* functions that combine functions into new functions.

This workshop presents higher-order functional programming in Python.   Python is the most popular programming language and it supports functional programming very well.

There are other programming which are specifically functional, such as Lisp and Haskel. 

Conventions:

- `f`, `g`, `h` are _*variables*_ referencing a function _*value*_.

"""

"""
----
"""

"""
# Types

This workshop will use Python's `typing` framework.

This workshop will use "type annotations" throughout.

Types are not required in Python nor necessary for the concepts described here.

Types help us understand functions in more detail:

- what they are
- what they do
- how they do it
- how they "should" be used

Resources:

- Python [typing](https://docs.python.org/3.13/library/typing.html) documentation.
"""

"""
## Type Annotations

Type Annotations are how we define how we intend to use a function.

Let's start with an untyped function:
"""

def f(a, b):
  "Return both a AND a times b."
  return (a, a * b)

f("Bob!", 3)
f([1, 2], 3)

"""
## Types

The `typing` module supports basic types and means to combine them:

* `int` - an integer
* `str` - a string
* `None` - no value; an optional value or when a function returns _**nothing**_

Abstract types:

* `Any` - any value
* `List` - a list of anything - `[2, 3.5, "alice"]`
* `List[int]` - a `list` containing `int`s : `[2, 3, 5]`
* `Tuple[float, str]` - a `tuple` containing a `float` and a `str` : `(2.3, "bob")`
"""

"""
## Function Types

Function types define function "signatures":

- the type of each parameter
- the type of the returned value or none at all
"""

"""
This is a more precise type declaration of `f`:
"""

def f(a: str, b: int) -> Tuple[str, int]:
  "Return both a AND a times b."
  return (a, a * b)

f("Bob!", 3)  # OK


"""
- `f()` has two arguments : `a` and `b`
- `a: str`                : `a` is a `str`
- `b: int`                : `b` is a `int`
- `-> Tuple[str, int]`    : returns a `str` and `int` in a `tuple`

_**Important Note**_

- Python types are not enforced.
- Type annotations are a guide for humans and tools.
- Even though `a` is declared `a: str`, in reality, any value that supports `a * b` will work.
"""

f([1, 2], 3)

"""
# Function Types
"""

"""
All functions have the type `typing.Callable` - meaning they can be "called", e.g: `f("ab", 21)`.
Methods are also `Callable` - that will be covered in more detail.

Functions can be annotated with increasing precision.

Any function with any arguments of any type and any return value - `f(a, b)` is in this category:

- `Callable` 
- `Callable[..., Any]`

But we can be more precise.  Based on its annotations, `f(a, b)` conforms to these types:

- `Callable[[str, int], Any]`
- and most precisely `Callable[[str, int], Tuple[str, int]]`

Abstractly:

* `Callable` - anything that can be called with zero or more arguments
* `Callable[[A1, A2], T]` - Two arguments of type `A1` and `A2`, respectively, returning type `T`

Functions with specific return types:

* `Callable[..., T]` - a `Callable` with zero or more arguments that returns a value of type `T`
* `Callable[[A1, A2], T]` - Two arguments of type `A1` and `A2`, respectively, returning type `T`
"""

"""
## Common Function Types

We can declare our own function types.  These are common:
"""

# Function with one argument that returns anything.
Unary = Callable[[Any], Any]

# Functions with two arguments that return anything.
Binary = Callable[[Any, Any], Any]

# Functions with zero or more arguments that return anything.
Variadic = Callable[..., Any]

"""
----
"""

"""
# First-Class Functions
"""

"""
Python functions are "first-class" functions; they are values just like `str`, `int`, `list` or `dict` values:

* assigned to variables
* stored in data structures
* arguments to functions
* returned from functions
"""

"""
## Functions don't have Names, Names have Functions!

In reality, `print` is a global variable:
"""

print
print(2)

g = print
g
g(2)

"""
## Where did that function come from?
"""

def call_func_three_times(func: Callable):
  for x in range(3):
    func(x)

call_func_three_times(print)

g = print
call_func_three_times(g)

"""
## The most useful useless function

The "identity" function is a placeholder.
"""

def identity(x: Any) -> Any:
  'Returns the first argument.'
  return x

identity
identity(2)
h = identity
h
h(3)

call_func_three_times(identity)  # DOES NOTHING!

"""
## Anonymous Functions

A `lambda` expression is function _**value**_ without a name.
"""

lambda x: x + 3                # Is a value!
(lambda x: x + 3)(2)           # Never had a name.

"""
 Lambdas functions can be stored in a variable, just like any other -- Python functions are "first-class" values.
"""

plus_three = lambda x: x + 3
plus_three
plus_three(2)

"""
----
"""

"""
# Closures
"""

"""
* Functions with closure are information hiders.
* They have access to values that not visible outside of them.
* They "close over (hidden) variables".
"""

"""
## Stateless Closures
"""

"""
### Constantly return the same value

This is placeholder, similar to `identity`:
"""

def constantly(val: Any) -> Callable[[], Any]:
  'Returns a function that returns a constant value without any arguments.'
  return lambda : val

constantly_5 = constantly(5)
constantly_5()
constantly_5()

# Fails with arguments:
try:
  constantly_5(13, 17)
except Exception as exc:
  exc

"""
### A more robust version
"""

def constantly(x: Any) -> Variadic:
  'Returns a function that returns a constant value and ignores all arguments.'
  return lambda *_args, **_kwargs: x

constantly_7 = constantly(7)
constantly_7()
constantly_7(13, foo=17)   # ignores all arguments

"""
----
"""

"""
# Adapters

Adapters are functions that create functions for expressions that are not directly `Callable`.
"""

"""
## Indexable Getters
"""

# A value `x` that supports `x[i]`:
Indexable = Union[List, Tuple, Dict]

def indexed(x: Indexable) -> Unary:
  'Returns a function `f(i)` that returns `x[i]`.'
  return lambda i: x[i]

a = ['a', 'b', 'c', 'd']
s = "012345"
d = {2: "two", 3: "three"}
indexed(s)(2)
indexed(a)(2)
indexed(d)(2)

# The inverse of `indexed`:
def at(i: Any) -> Unary:
  'Returns a function `f(x)` that returns `x[i]`.'
  return lambda x: x[i]

a = ['a', 'b', 'c', 'd']
s = "012345"
d = {2: "two", 3: "three"}
at(2)(s)
at(2)(a)
at(2)(d)

"""
## Object Accessors
"""

@dataclass
class Position:
  "A 2D position."
  x: int = 0
  y: int = 0

p = Position(2, 3)
p

def getter(name: str) -> Callable[[Any], Any]:
  return lambda obj: \
    getattr(obj, name)

g = getter('x')
g(p)

def object_get(obj: Any) -> Callable[[str], Any]:
  return lambda name: \
    getattr(obj, name)

h = object_get(p)
h('y')

# Positions do not have a `z` attribute:
try:
  h('z')
except AttributeError as x:
  print(repr(x))

def setter(name: str) -> Unary:
  "Can set `name`."
  return lambda obj, val: \
    setattr(obj, name, val)

def accessor(name: str) -> Callable[[Any, Optional[Any]], Any]:
  "Can get and set `name`."
  def g(obj, *val):
    if val:
      return setattr(obj, name, val[0])
    return getattr(obj, name)
  return g

s = setter('x')
s(p, 11)
p

a = accessor('x')
a(p)
a(p, 13)
p

"""
## Other Adapters
"""

def projection(key: Any, *default) -> Callable:
  'Returns a function `f(a)` that returns `a.get(key, default)`.'
  return lambda a: a.get(key, *default)

p = projection("a", 999)
p({"a": 2, "b": 3})
p({})

"""
----
"""

"""
# Stateful Closures

Stateful closures are functions that have access to state that is not visible outside the function.
"""

"""
## Generators

A generator is an "impure" closure, which may return a different value regardless of its arguments.

Examples:

- functions that count
- functions that generate random numbers
- functions that read the next line in a file
"""

def counter(start: int = 0, increment: int = 1) -> Callable[[], int]:
  "Generator of arithmetic sequences."
  i = start - increment      # <== STATE
  def g() -> int:
    nonlocal i               # <== CLOSED OVER STATE
    i += increment           # <== STATE IS CHANGED.
    return i
  return g                   # <== NEW FIRST-ORDER FUNCTION

c = counter(2, 3)
c()
c()
c()

"""
----
# The End
----
"""
