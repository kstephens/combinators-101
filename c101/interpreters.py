#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


import sys; sys.path.append('..')
from c101.helpers import *


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
    return reduce(trace(eval), map(trace(parse), program.split(" ")), [])

stacky("2 3 *", trace)
stacky("2 3 5 + *")
stacky("33 2 3 + 5 * >")


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


# ----
# # The End
# ----
