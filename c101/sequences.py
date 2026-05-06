# %%capture import_io
from typing import Callable
from c101.helpers import *
from c101.combinators_101 import *
from c101.combinators_101 import constantly_7
from c101.combinators import not_, with_counter, partial
from c101.parser_combinators import is_string

"""
# Sequences

We will show common sequence operations
"""

"""
----
"""

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

# Functions with two arguments that return anything.
Binary = Callable[[Any, Any], Any]

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
----
# The End
----
"""
