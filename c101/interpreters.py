# %%capture import_io
from c101.helpers import *
import c101.helpers
from c101.combinators_101 import *
from functools import reduce
map = c101.helpers.map_

"""
# Interpreters
"""

import operator

def stacky(program, trace=identity):
    'A stack-oriented expression evaluator.'
    def eval(stack, item):
        if isinstance(item, int):
            return stack + [item]
        return stack[:-2] + [item(stack[-2], stack[-1])]
    def parse(word):
        if re.match(r'-?\d+', word):
            return int(word)
        return getattr(operator, word)
    return reduce(trace(eval), map(trace(parse), program.split(" ")), [])

stacky("2 3 mul", trace)

stacky("2 3 5 add mul", trace)

stacky("33 2 3 add 5 mul gt")

"""
----
# The End
----
"""
