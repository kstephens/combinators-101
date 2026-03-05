#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


get_ipython().run_cell_magic('capture', 'import_io', "import sys; sys.path.append('..')\nfrom c101.helpers import *\nimport c101.helpers\nfrom c101.combinators_101 import *\nfrom functools import reduce\nmap = c101.helpers.map_\n")


# # Interpreters

# In[9]:


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


# In[10]:


stacky("2 3 5 add mul", trace)


# In[11]:


stacky("33 2 3 add 5 mul gt")


# ----
# # The End
# ----
