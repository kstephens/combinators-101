from typing import Callable
from c101.helpers import *
from c101.combinators import trace

"""
# Decorators

Python Decorators are combinators!
"""

"""
----
"""

@trace
def this_function(x):
    return x * 3

this_function(5)

"""
----
# The End
----
"""
