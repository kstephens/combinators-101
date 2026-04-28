"""
# (Imports)
"""

# %%capture import_io
import sys; sys.path.append('..')
from c101.helpers import *
import c101.helpers
from c101.combinators_101 import *
from functools import reduce
map = c101.helpers.map_

"""
## Operator Predicates
"""


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

# Create a table where `x OP y` is true:
[
  f'{x} {op} {y}'
  for op in ['<', '==', '>']
  for x in (2, 3, 5)
  for y in (2, 3, 5)
  if binary_op(op)(x, y)
]

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

h = op_pred(">", 3)
h(2)
h(5)

g = op_pred("~=", 'ab+c')
g('')
g('ab')
g('abbbcc')

"""
----
# The End
----
"""
