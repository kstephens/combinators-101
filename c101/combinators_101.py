#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[1]:


import sys; sys.path.append('..')
from c101.helpers import *


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

# ----

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

# In[2]:


# Example:
# A `Callable` that has 2 parameters,
#   an `str` and `int`
#   and returns a `Tuple` of `int` and `int`:
Callable[[str, int], Tuple[int, int]]

def h(a: str, b: int) -> Tuple[int, int]:
  return (len(a), len(a) * b)

h("ab", 21)


# ----

# # First-Class Functions

# can be:
# 
# * assigned to variables
# * arguments to functions
# * returned as values

# ## Functions don't have Names, Names have Functions!

# In[3]:


print(2)
g = print
g
g(2)


# ## Where did that function come from?

# In[4]:


def call_func_three_times(func: Callable):
  for x in range(3):
    func(x)

call_func_three_times(print)


# In[5]:


call_func_three_times(g)


# ## The most useful useless function

# In[6]:


def identity(x: Any) -> Any:
  'Returns the first argument.'
  return x

identity(2)
h = identity
h
h(3)


# ## Anonymous Functions

# In[7]:


lambda x: x + 3
(lambda x: x + 3)(2)           # Never had a name.


# In[8]:


plus_three = lambda x: x + 3   # Gave it a name.
plus_three
plus_three(2)


# ----

# # Closures

# * Functions with closure are information hiders.
# * They have access to values that are otherwise not visible outside of them.
# * They "close over variables".

# ## Stateless Closures

# ### Constantly return a value

# In[9]:


def constantly(val: Any) -> Callable[[], Any]:
  return lambda : val


# In[10]:


constantly_5 = constantly(5)
constantly_5()
constantly_5()


# In[11]:


# Fails with arguments
try:
  constantly_5(13, 17)
except Exception as exc:
  exc


# ### A more robust version

# In[12]:


# Functions with zero or more arguments that return anything.
Variadic = Callable[..., Any]

def constantly(x: Any) -> Variadic:
  'Returns a function that returns a constant value.'
  return lambda *_args, **_kwargs: x

constantly_7 = constantly(7)
constantly_7


# In[13]:


constantly_7()


# In[14]:


constantly_7(13, 17)


# ----

# # Adapters

# ## Indexable Getters

# In[15]:


# Function with one argument that returns anything.
Unary = Callable[[Any], Any]

# A value `x` that supports `x[i]`:
Indexable = Union[List, Tuple, Dict]


# In[16]:


def at(i: Any) -> Unary:
  'Returns a function `f(x)` that returns `x[i]`.'
  return lambda x: x[i]

a = ['a', 'b', 'c', 'd']
f = at(2)
f(a)


# In[17]:


def indexed(x: Indexable) -> Unary:
  'Returns a function `f(i)` that returns `x[i]`.'
  return lambda i: x[i]

a = ['a', 'b', 'c', 'd']
f = indexed(a)
f(2)


# #### Works with Strings and Dicts

# In[18]:


s = "abcdef"
indexed("abcdef")(4)
at(3)(s)


# In[19]:


d = {"a": 2, "b": 3}
indexed(d)("b")
at("b")(d)


# ## Object Accessors

# In[20]:


@dataclass
class Position:
  "A 2D position."
  x: int = 0
  y: int = 0

p = Position(2, 3)
p


# In[21]:


def getter(name: str, *default) -> Callable[[Any], Any]:
  return lambda obj: \
    getattr(obj, name, *default)

def object_get(obj: Any) -> Callable[[str], Any]:
  return lambda name, *default: \
    getattr(obj, name, *default)


# In[22]:


g = getter('x')
g(p)


# In[23]:


h = object_get(p)
h('x')
h('z', 999)


# In[24]:


# Positions do not have a `z` attribute:
try:
  h('z')
except AttributeError as x:
  print(repr(x))


# In[25]:


def setter(name: str) -> Unary:
  return lambda obj, val: setattr(obj, name, val)

def accessor(name: str) -> Callable[[Any, Optional[Any]], Any]:
  def g(obj, *val):
    if val:
      return setattr(obj, name, val[0])
    return getattr(obj, name)
  return g


# In[26]:


s = setter('x')
s(p, 5)
p


# In[27]:


a = accessor('x')
a(p)
a(p, 7)
p


# ## Other Adapters

# In[28]:


def projection(key: Any, *default) -> Callable:
  'Returns a function `f(a)` that returns `a.get(key, default)`.'
  return lambda a: a.get(key, *default)

p = projection("a", 999)
p({"a": 2, "b": 3})
p({})


# ----

# # Stateful Closures
# 
# Stateful closures are functions that have access to state that is not visible outside the function.

# ### Generators
# 
# A generator is an impure function, which may return a different value regardless of its arguments.
# Examples:
# - random number generator
# - reading lines from a file 

# In[29]:


def counter(start: int = 0, increment: int = 1) -> Callable[[], int]:
  "Generator of arithmetic sequences."
  i = start - increment
  def g() -> int:
    nonlocal i
    i += increment
    return i
  return g

c = counter(2, 3)
c()
c()
c()


# ----

# # Second-Order Functions

# Second-Order Functions return other functions.
# 
# Often have the form:
# 
# ```python
# def f(a: Any, ...):
#   # g() has access to a:
#   def g(b: Any, ...):
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
# ```python
# def c(f: Callable, ...) -> Callable:    # <-- COMBINATOR
#   def g(b, ...):                        # <-- COMPOSITION
#     return f(do_something_with(a, b))   # <-- APPLICATION and RESULT
#   return g                              # <-- CLOSURE
# ```
# 
# or for brevity:
# 
# ```python
# def c(f: Callable, ...) -> Callable:
#   return lambda b, ...: f(do_something_with(a, b))
# ```

# ----

# # Stateless Combinators

# ### Tracing Combinator
# 
# Wrap a function with tracing information:

# In[30]:


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


# ----

# # Stateful Combinators

# In[31]:


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

# In[103]:


trace_indent = 0                                             # <-- GLOBAL STATE

def trace(f: Callable, name: str | None = None) -> Callable:
    "Wrap a function that logs input and output."
    name = name or f.__name__                                # <-- LOCAL STATE
    def g(*args, **kwargs):                                  # <-- COMPOSITION
        global trace_indent                                  # <-- GLOBAL STATE
        g, _ = "\033[38;5;22m", "\033[0m"
        r = "\033[38;2;120;50;50m"
        g = "\033[38;2;40;180;40m"
        b = "\033[38;2;120;120;255m"
        ind = f"{g}\u21e2 {"\u2502 " * trace_indent}"
        print(f"{ind}{_}{format_args(name, args, kwargs)}")
        try:
            trace_indent += 1
            result = f(*args, **kwargs)                      # <--- APPLICATION
        except Exception as exc:
            print(f"{ind}{_}{r}\u2570\u2574\u29b8 {exc!r}{_}")
            raise exc
        finally:
            trace_indent -= 1
        print(f"{ind}\u2570\u2574{_} {b}{result!r}{_}")
        return result                                        # <--- RESULT
    return g                                                 # <--- CLOSURE

add = trace(lambda x, y: x + y, "add")
avg = trace(lambda x, y: add(x, y) / (2.0 * y), "avg")
trace(avg)(2, 3)
try:
    trace(avg)(2, 0)
except:
    pass


# ----

# # Predicates

# In[33]:


# Functions with zero or more arguments that return a boolean.
Predicate = Callable[..., bool]

def is_string(x: Any) -> bool:
  'Returns true if `x` is a string.'
  return isinstance(x, str)

is_string("hello")
is_string(3)


# # Function Composition
# 
# Function Composition is when functions are combinined into new forms.

# # Predicate Combinators

# In[34]:


# Functions that take a Predicate and return a new Predicate.
PredicateCombinator = Callable[[Predicate], Predicate]

def not_(f: Predicate) -> Predicate:
  'Returns a function that logically negates the result of the given function.'
  return lambda *args, **kwargs: not f(*args, **kwargs)

g = not_(is_string)
g("hello")
g(3)


# # Partial Application
# 
# Partial application adds "default" arguments.

# ## Methods are Partially Applied Functions
# 
# The first argument of a method is the receiver.
# 
# The method is said to be "bound" to the object.
# 
# In other words, a method is a function partially applied to its receiver.

# In[35]:


a = 2
b = 3
a + b
a.__add__(b)    # eqv. to `a + b`
f = a.__add__
f               # h is the partial application of (2).__add__
f(b)


# ## Generic Partial Application

# In[36]:


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


# In[37]:


def partial_right(f: Callable, *args, **kwargs) -> Callable:
  'Returns a function that appends `args` and merges `kwargs`.'
  def g(*args2, **kwargs2):
    return f(*(args2 + args), **(kwargs2 | kwargs))
  return g

def add_and_multiply(a, b, c):
  return (a + b) * c

add_and_multiply(2, 3, 5)

g = partial_right(add_and_multiply, 2)
g(3, 5)


# # Composition

# In[38]:


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

g = repr
f = str
h = compose(g, f)
h("abc")
h(5)


# In[39]:


def multiply_by_3(x):
  return x * 3

plus_three(multiply_by_3(5))

h = compose(plus_three, multiply_by_3)
h(5)


# In[40]:


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


# # Iterative Combinators

# In[70]:


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


# In[ ]:


def Heron(S: float) -> float:
    def g(x):
        return (x + S / x) / 2.0
    return g

def sqrt(S: float) -> float:
    S = float(S)
    return fixed_point(trace(Heron(S)))(S / 2)

math.sqrt(2.0)
sqrt(50.0)
math.sqrt(50.0)


# In[71]:


def Collatz(n):
    if n == 1:
        return n
    return n // 2 if n % 2 == 0 else n * 3 + 1
fixed_point(trace(Collatz))(88)


# # Manipulating Sequences

# ## Mapping functions over sequences

# In[45]:


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


# In[46]:


# Restore the built-in:
# map = map_


# ## Filtering Sequences with Predicates

# In[47]:


def filter(f: Unary, xs: Iterable) -> Iterable:
  'Returns a sequence of the elements of `xs` for which `f` returns true.'
  return [x for x in xs if f(x)]

items = [1, "string", False, True, None]
filter(is_string, items)
filter(not_(is_string), items)


# ## Reducing Sequences with Binary Functions

# In[48]:


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


# In[49]:


items = [1, "string", 2, 3, "-and-more", 5]

# Concat all strings:
reduce(add, filter(is_string, items), "")

# Sum of all numbers:
def is_number(x: Any) -> bool:
  return not isinstance(x, bool) and isinstance(x, Number)
reduce(add, filter(is_number, items), 0)

# Sum all non-strings:
reduce(add, filter(not_(is_string), items), 0)


# In[50]:


def conjoin(a, b) -> Callable[[Any, Any], Tuple[Any, Any]]:
  'Creates a Tuple from two arguments.'
  return (a, b)

items = [3, "a", 5, "b", 7, "c", 11, True]
reduce(conjoin, items, 2)

dict(map(with_counter(conjoin, 21), ["a", "b", "c", "d"]))


# ## Map as a Reduction

# In[51]:


def map_r(f: Unary, xs: Iterable) -> Iterable:
  def acc(seq, x):
    return seq + [f(x)]
  return reduce(acc, xs, [])

map(plus_three, [3, 5, 7, 11])
map_r(plus_three, [3, 5, 7, 11])


# ## Filter as a Reduction

# In[52]:


def filter_r(f: Unary, xs: Iterable) -> Iterable:
  def acc(seq, x):
    return seq + [x] if f(x) else seq
  return reduce(acc, xs, [])

items
filter(is_string, items)
filter_r(is_string, items)


# ## Mapcat (aka Flat-Map)

# In[53]:


ConcatableUnary = Callable[[Any], Iterable]

def mapcat(f: ConcatableUnary, xs: Iterable):
  'Concatenate the results of `map(f, xs)`.'
  return reduce(add, map(f, xs), [])

def duplicate(n, x):
  return [x] * n

duplicate_each_3_times = partial(mapcat, partial(duplicate, 3))
duplicate_each_3_times([".", "*"])
duplicate_each_3_times(range(4, 7))


# ## Manipulating Arguments

# In[54]:


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


# # Interlude

# In[55]:


def modulo(modulus: int) -> Callable[[int], int]:
  return lambda x: x % modulus

mod_3 = modulo(3)
map(mod_3, range(10))


# In[56]:


h = compose(indexed(a_list_of_strings), mod_3)
a_list_of_strings
map(h, range(10))


# ### Arity Reduction

# In[57]:


def unary(f: Variadic) -> Unary:
  return lambda *args, **kwargs: f((args, kwargs))

h = unary(identity)
h()
h(1)
h(1, 2)
h(a=1, b=2)


# # Developer Affordance

# ## Error Handlers

# In[58]:


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


# # Logical Combinators

# ## Predicators

# In[59]:


def re_pred(pat: str, re_func: Callable = re.search) -> Predicate:
  'Returns a predicate that matches a regular expression.'
  rx = re.compile(pat)
  return lambda x: re_func(rx, str(x)) is not None

re_pred("ab")("abc")
re_pred("ab")("nope")


# In[60]:


def default(f: Variadic, g: Variadic) -> Variadic:
  def h(*args, **kwargs):
    if (result := f(*args, **kwargs)) is not None:
      return result
    return g(*args, **kwargs)
  return h


# asdf

# ## Logical Predicate Composers

# In[61]:


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


# In[62]:


Procedure = Callable[[], Any]

def if_(f: Variadic, g: Unary, h: Unary) -> Variadic:
  def i(*args, **kwargs):
    if (result := f(*args, **kwargs)):
      return g()
    return h()
  return i


# ----

# ## Sequencing

# In[63]:


def progn(*fs: Iterable[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = None
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g


# In[64]:


def prog1(f0: Callable, *fs: Iterable[Callable]) -> Callable:
  'Returns a function that calls each function in turn and returns the last result.'
  def g(*args, **kwargs):
    result = f0(*args, **kwargs)
    for f in fs:
      result = f(*args, **kwargs)
    return result
  return g


# In[65]:


def reverse_apply(x: Any) -> Callable:
  return lambda f, *args, **kwargs: f(x, *args, **kwargs)

reverse_apply(1) (plus_three)


# ----
# # The End
# ----
