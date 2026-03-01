#!/usr/bin/env python
# coding: utf-8

# # (Imports)

# In[ ]:


import sys; sys.path.append('..')
from c101.helpers import *


# # Types

# In[ ]:


# Functions with zero or more arguments that return anything.
Variadic = Callable[..., Any]

# Function with one argument that returns anything.
Unary = Callable[[Any], Any]

# A value `x` that supports `x[i]`:
Indexable = Union[List, Tuple, Dict]

Predicate = Callable[..., bool]


# # Parser Combinators

# In[ ]:


# Parser input: a sequence of lexemes:
Input = Sequence[Any]

# A parsed value and remaining input:
Parsed = Tuple[Any, Input]

# A parser matches the input sequence and produces a result or nothing:
Parser = Callable[[Input], Parsed | None]


# In[ ]:


def at(i: Any) -> Unary:
  'Returns a function `f(x)` that returns `x[i]`.'
  return lambda x: x[i]


# In[ ]:


def show_match(p: Parser) -> Variadic:
  def g(input: Input):
    return (p(input) or False, '<=', input)
  return g


# In[ ]:


first = at(0)
def rest(x: Input) -> Input:
  return x[1:]

def equals(x) -> Parser:
  'Returns a parser that matches `x`.'
  def g(input: input):
    y = first(input)
    logging.debug("equals(%s, %s)", repr(x), repr(y))
    if x == y:
      return y, rest(input)
  return g

h = equals('a')
h(['a'])
h(['b', 2])


# In[ ]:


def which(p: Predicate) -> Parser:
  'Returns a parser for the next lexeme when `p(lexeme)` is true.'
  def g(input: Input):
    if p(first(input)):
      return (first(input), rest(input))
  return g

def is_string(x: Any) -> bool:
  return isinstance(x, str)

def is_number(x: Any) -> bool:
  return isinstance(x, (int, float))

g = which(is_string)
g(['a'])
g([2])
g(['a', 'b'])

def alternation(*ps) -> Parser:
  def g(input):
    for p in ps:
      if (result := p(input)):
        return result
  return g

g = alternation(which(is_string), which(is_number))
g(['a'])
g([2])
g([False])


# # Sequence Parsers

# In[ ]:


ParsedSequence = Tuple[Sequence, Input]
SequenceParser = Callable[[Input], ParsedSequence | None]

def one(p: Parser) -> SequenceParser:
  'Returns a parser for one lexeme.'
  def g(input: Input):
    if input and (result := p(input)):
      parsed, input = result
      return [parsed], input
  return g

g = one(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])


# In[ ]:


def zero_or_more(p: Parser) -> SequenceParser:
  'Returns a parser for zero or more lexemes.'
  def g(input: Input):
    acc = []
    while input and (result := p(input)):
      parsed, input = result
      acc.append(parsed)
    return acc, input
  return g

g = zero_or_more(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


def one_or_more(p: Parser) -> SequenceParser:
  'Returns a parser for one or more lexemes as a sequence.'
  p = zero_or_more(p)
  def g(input: Input):
    if (result := p(input)) and len(result[0]) >= 1:
      return result
  return g


# In[ ]:


g = one_or_more(which(is_string))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


def sequence_of(*parsers) -> SequenceParser:
  'Returns a parser for parsers of a sequence.'
  def g(input: Input):
    acc = []
    for p in parsers:
      if result := p(input):
        parsed, input = result
        acc.extend(parsed)
      else:
        return None
    return acc, input
  return g

g = sequence_of(one(which(is_string)), one(which(is_string)))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 'b', 2])
g(['a', 'b', 3, 5])


# In[ ]:


g = sequence_of(one_or_more(which(is_number)))
g([])
g(['a'])
g([2])
g([2, 3])
g([2, 3, False])


# In[ ]:


g = sequence_of(one(which(is_string)), one_or_more(which(is_number)))
g([])
g(['a'])
g([2])
g(['a', 'b'])
g(['a', 2])
g(['a', 2, 3])
g(['a', 2, 'b', 3])
g(['a', 2, 3, False])
g(['a', 2, 3, False, 'more'])


# # Parser Grammar

# In[ ]:


def take_while(f: Unary) -> Unary:
  def g(seq):
    acc = []
    while seq and (x := f(seq[0])):
      acc.append(x)
    return acc
  return g

def action(p: Parser, f: Callable[[Any], Any]) -> Parser:
  'Returns a parser that calls `f` with parsed value.'
  def g(seq):
    if result := p(seq):
      return a(result[0]), result[1]
  return g

env = {}
def a(v):
  # nonlocal x
  env['x'] = v
  return v
f = action(which(is_string), a)
f(["abc"])
env


# # Lexical Scanning

# In[ ]:


def eat(rx: str):
  p = re.compile(rx)
  return lambda s: re.sub(p, '', s)

def lexeme(pat: str, post = at(0)):
  post = post or (lambda m: m[0])
  rx = re.compile(pat)
  ws = eat(r'^\s+')
  def g(input):
    input = ws(input)
    if input and (m := re.match(rx, input)):
      return post(m), input[len(m[0]):]
  return g


# In[ ]:


def grammar_parser():
  env = {}
  def _(id):
    return lambda *args: env[id](*args)

  def action(p: Parser, action: Unary) -> Parser:
    def g(input: Input):
      if result := p(input):
        value = action(result[0])
        return value, result[1]
    return g

  def cache(p: Parser) -> Parser:
    '''
    Cache the result of p(input).
    This improves performance when a definition is
    parsed multiple times.
    '''
    d = {}
    def g(input):
      if v := d.get(id(input)):
        # logging.debug('cached : %s => %s', repr(input), repr(v[0]))
        return v[0]
      v = p(input)
      d[id(input)] = (v,)
      return v
    return g

  def definition(id, p, act=None):
    # p = trace(p, id)
    # p = cache(p)
    a = None
    if act is True:
      a = lambda x: (id, x)
    elif isinstance(act, str):
      a = lambda x: (act, x)
    elif act:
      a = act
    if a:
      p = action(p, a)
    p = cache(p)
    env[id] = p

  definition('string',        lexeme(r'^"(\\"|\\?[^"]+)*"',
                                lambda m: ('string', eval(m[0]))))
  definition('regex',         lexeme(r'^/((\\/|(\\?[^/]+))*)/',
                                lambda m: ('regex', re.compile(m[1]))))
  definition('name',          lexeme(r'^[a-zA-Z][a-zA-Z0-9_]*'))
  definition('terminal',      alternation(_("string"), _('regex')))
  definition('non_terminal',  _('name'),
                                lambda x: ('reference', x))
  definition('action',        lexeme(r'^@\{(.+?)\}@',
                                lambda m: ('action', m[1].strip())))
  definition('basic_match',   alternation(_('non_terminal'), _('terminal')))
  definition('bound_match',   sequence_of(one(_('basic_match')), one(lexeme(r'^:')), one(_('name'))),
                                lambda x: ('bound_match', x[0], x[2]))
  definition('match',         alternation(_('bound_match'), _('basic_match')))
  definition('matches',       one_or_more(_('match')))
  definition('matches_with_action', sequence_of(_('matches'), one(_('action'))))
  definition('pattern',       alternation(_('matches_with_action'), _('matches')))
  definition('sequence',      sequence_of(_('pattern')), lambda x: ('sequence', x))
  definition('alternation',   sequence_of(one(_('sequence')), one(lexeme(r'\|')), one(_('production'))),
                                lambda x: ('alternation', x[0], x[2]))
  definition('production',    alternation(_('alternation'), _('sequence')))
  definition('definition',    sequence_of(one(_('name')), one(lexeme(r"=")), one(_('production')), one(lexeme(r';'))),
                                lambda x: ('definition',  x[0], x[2]))
  definition('grammar',       sequence_of(one_or_more(_('definition'))), 'grammar')

  def g(input, start=None):
    return _(start or 'grammar')(input)
  return g


# In[ ]:


grammar_tests = [
  # [r'"asdf"'], # , 'pattern'],
  # [r'  a = "asdf";'],
  # [r'  a = b c;'],
  # [r'a =b c|d;'],
  # [r'a = b c | d | e f;'],
  # [r'a = "foo";'],
  [r'b = /^foo/:c @{ do_this(c) }@;'],
  # [r'a = b : x c : y @{ do_this(x, y) }@ ;'],
  [r'''
expr = mult | add | const;
mult = expr "*" expr;
add = expr "+" expr;
const = /^[-+]?\d+/;
  ''']
]

gram = grammar_parser()

for grammar_test in grammar_tests:
  logging.debug("============================================\n")
  ic(grammar_test)
  result = gram(*grammar_test)
  ic(result)


# # Grammar Compiler

# In[ ]:


def compile_grammar(gram, parser_name):
  gensym_i = 0
  def gensym(name):
    nonlocal gensym_i
    gensym_i += 1
    return f"__{name}__{gensym_i}"

  ref_cache = {}
  def ref(name):
    nonlocal ref_cache
    if x := ref_cache.get(name):
      return x
    x = ref_cache[name] = gensym(name)
    return x

  input = gensym('input')
  result = gensym('result')
  newlines = "\n\n"
  depth = 0

  stack = []
  def push():
    stack.append((input, result))

  def pop():
    input, result = stack.pop()

  def indent(s, chars):
    prefix = f"\n{' ' * chars}"
    return prefix.join(map(lambda s: f"{prefix}{x}", s.split("\n")))

  def advance(value, remaining = f"{result}[1]"):
    return f"""
    {result} = ({value}, {remaining})
    {input} = {result}[1]
  """

  def grammar(definitions):
    start_name = definitions[0][1]
    return f"""
def {parser_name}({input}):
{newlines.join(map(compile, definitions))}
  return {ref(start_name)}({input})
"""

  def definition(name, production):
    return f"""
  def {ref(name)}({input}):
    {result} = None
{compile(production)}
    return {result}
"""

  def alternation(*exprs):
    code = ""
    input_save = gensym('input')
    code += f"""
    {input_save} = {input}
"""
    for expr in exprs:
      code += compile(expr)
      push()
      result = gensym('result')
      code += f"""
{compile(expr)}
    if {result}:
      return {result}
    {input} = {input_save}
"""
      pop()
    code += f"""
      return {result}
"""
    return code

  def sequence(exprs):
    sequence = gensym('sequence')
    code = ""
    code += f"""
    {sequence} = []
"""
    for expr in exprs:
      code += f"""
{compile(expr)}
    if not {result}:
      return None
    {sequence}.append({result}[0])
{advance(sequence)}
"""
    return code

  def reference(name):
    return f"""
    {result} = {ref(name)}({input})
"""

  def patterns(exprs):
    return "\n".join(map(compile, exprs))

  def bound_match(expr, name):
    return f"""
{compile(expr)}
    {name} = {result} and {result}[0]
"""

  def matches_with_action(expr):
    ic(expr)
    return f"""
{compile(expr)}
    if {result}:
      return {indent(action, 6)}, {input}
"""

  def string(s):
    const = repr(s)
    check = f"({input}[0:{len(s)}] == {const})"
    return f"""
    if not {check}:
      return None
{advance(const, f"{input}[:{len(s)}]")}
"""

  def integer(expr):
    match = gensym('match')
    return f"""
    if not ({match} := re.search(r'^([-+]?\\d+)', {input})):
      return None
{advance(f"int({match}[1])", f"{input}[:len({match}[1])]")}
"""

  def regex(expr):
    match = gensym('match')
    return f"""
    if not ({match} := {expr!r}.search({input}):
      return None
{advance(f"{match}[1]", f"{input}[0:len({match}[1])]")}
"""

  def action(code):
    # ic(("action", code))
    return f"""
    {result} = ({code})
{advance(result, input)}
"""

  funcs = locals()
  def compile(expr):

    # ic(("compile", expr))
    nonlocal depth
    depth += 1
    indent = '  ' * depth
    result = funcs[expr[0]](*expr[1:])
    depth -= 1
    indent = '  ' * depth
    result = f"{indent}### {expr!r}\n{result}"
    result = "\n".join([line for line in result.splitlines() if line])
    return result
    return f"""
{indent}####################################
{indent}# {repr(expr)} (((
{result}
{indent}# {repr(expr)} )))
{indent}####################################
"""

  return compile(gram)

gram = grammar_parser()
for i, grammar_test in enumerate(grammar_tests):
  print("")
  print("### ============================================")
  print(f"''' {grammar_test[0]} '''")
  # ic(grammar_test)
  grammar_parsed = gram(*grammar_test)[0]
  print(f"''' {grammar_parsed!r} '''")
  # ic(grammar_parsed)
  print(compile_grammar(grammar_parsed, f"parser_{i}"))
  print("### ============================================")


# ----
# # The End
# ----
