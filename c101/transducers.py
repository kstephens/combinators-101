#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[1]:


get_ipython().run_cell_magic('capture', 'import_io', "import sys; sys.path.append('..')\nfrom c101.helpers import *\nfrom c101.combinators_101 import *\nimport operator as op\nimport inspect\n")


# # Transducers
# 
# _** WORK IN PROGRESS **_
# 
# Resources
# 
# - https://clojure.org/reference/transducers
# - https://www.youtube.com/watch?v=6mTbuzafcII
# - http://www.cs.ox.ac.uk/files/3390/PRG69.pdf
# - https://people.cs.nott.ac.uk/pszgmh/fold.pdf
# 

# ----

# In[5]:


def map_seq(f: Unary, seq: Iterable):
    for x in seq:
        yield f(x)

def mapcat_seq(f: Unary, seq: Iterable):
    for x in seq:
        for e in f(x):
            yield e

def reduce_seq(f: Binary, init: Any, seq: Iterable):
    for x in seq:
        init = f(init, x)
    return init

reduce_seq(op.add, 0, map_seq(op.neg, (1, 2, 3)))
list(mapcat_seq(list, ((2, 3), (5, 7, 11, (13, 17)))))


# # Creating Transducers
# 
# Tranducers follow this form:
# 
# ```python
# def g(rf: ReductionFunction):
#   def h(*args):
#     def init():
#       return ...
#     def step(x, y):
#       return ...
#     def completion(x):
#       return ...
#     def t(*args):
#       if len(args) == 0:
#         return init()
#       if len(args) == 2:
#         return step(*args)
#       if len(args) == 1:
#         return completion(*args)
#       raise TypeError("invalid transduction")
#   return h
# ```

# In[3]:


def transduce_4(xform, f, init, coll):
  f = xform(f)
  ret = WhatWhatWhat
  return f(ret)

transduce = arity(
  lambda xform, f, coll: transduce(xform, f, f(), coll),
  lambda xform, f, init, coll:
    transduce_4(xform, f, init)
)

completing = arity(
    lambda f: completing(f, identity),
    lambda f, cf:
      arity(
        lambda: f(),
        lambda x: cf(x),
        lambda x, y: f(x, y)
      )
)


# In[4]:


map = arity(
  lambda f:
    lambda rf:
      arity(
        lambda: rf(),
        lambda result: rf(result),
        lambda result, input: rf(result, f(input)),
      ),
    map_seq,
)
list(map(op.neg, (2, 3, 5)))
map(op.neg)
transduce(map(op.neg))


# # Examples

# In[ ]:


def dedupe()
  prev = None
  def g(xf):
    prev = None
    def h(*args):
      if len(args) == 0:  # init
        return xf()
      if len(args) == 1:  # step
        result = *args
        return xf(result)
      if len(args) == 2:
        result, input = *args
        prior = prev
        prev = input
        if prior == input:
          return result
        return xf(result, input)
    return g


# 
# ----
# IGNORE
# ----

# In[ ]:


def partial(f: Callable, *args) -> Callable:
    args = list(args)
    def g(*more_args):
        return f(*(args + list(more_args)))
    return g


# In[ ]:


def tmap(f: Unary, *args) -> Callable | Any:
    if len(args) == 0:
        return partial(map, f)
    return map(f, *args)

def treduce(f: Binary, init: Any, *args):
    if len(args) == 0:
        return partial(reduce, f, init)
    return reduce(f, init, *args)


# In[ ]:


def transductor(init, step, completion):
  def h(*args):
    def t(*args):
      if len(args) == 0:
        return init()
      if len(args) == 2:
        return step(*args)
      if len(args) == 1:
        return completion(*args)
      raise TypeError("invalid transduction")
    return t
  return h


# In[ ]:


neg = tmap(op.neg)
sum = treduce(op.add, 0)
concat = treduce(op.add, "")
pipeline = compose(concat, str, sum, neg)
pipeline((2, 3, 5))


# ----
# # The End
# ----
