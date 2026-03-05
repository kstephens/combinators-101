#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


get_ipython().run_cell_magic('capture', 'import_io', "import sys; sys.path.append('..')\nfrom c101.helpers import *\nimport c101.helpers\nfrom c101.combinators_101 import *\nfrom functools import reduce\nmap = c101.helpers.map_\n")


# ## Operator Predicates

# In[3]:


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
  f.__qualname__ = f"binary_op({n!r})"

binary_op('==') (2, 2)
binary_op('!=') (2, 2)


# In[4]:


# Create a table where `x OP y` is true:
[
  f'{x} {op} {y}'
  for op in ['<', '==', '>']
  for x in (2, 3, 5)
  for y in (2, 3, 5)
  if binary_op(op)(x, y)
]


# In[5]:


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


# In[6]:


h = op_pred(">", 3)
h(2)
h(5)


# In[7]:


g = op_pred("~=", 'ab+c')
g('')
g('ab')
g('abbbcc')


# ----
# # The End
# ----
