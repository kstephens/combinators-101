from typing import Any, Optional, Union, List, Tuple, Dict, Iterable, Mapping, Callable, Type, Literal, IO, NoReturn, Self
from numbers import Number
from icecream import ic


class SeqError(Exception):
   pass


class Seq():
   def empty(self) -> bool:
      return False
   def first(self) -> Any | NoReturn:
      raise SeqError()
   def rest(self) -> Self | NoReturn:
      raise SeqError()
   def _simplify(self):
      return self
   def __repr__(self):
      return f"sq.{type(self).__qualname__}(...)"

class EmptyType(Seq):
   def empty(self) -> bool:
      return True
   def __repr__(self):
      return "sq.null"
null = EmptyType()

def empty(seq):
   return seq is null or seq.empty()
def first(seq):
   return seq.first()
def rest(seq):
   return seq.rest()

def coerce_to_seq(seq):
   if not isinstance(rest, Seq):
      return iterable(seq)
   return seq

# def simplify(seq):
#    if seq.empty():
#       return null
#    return seq

def cons(first, rest):
   rest = coerce_to_seq(rest)
   return Cons(first, rest)
def cons_list(itr):
   head = tail = Cons(null, null)
   for x in itr:
      tail._rest = Cons(x, null)
      tail = tail._rest
   return head._rest
class Cons(Seq):
   def __init__(self, first, rest):
      self._first = first
      self._rest = rest
   def first(self):
      return self._first
   def rest(self):
      return self._rest


class Lazy(Seq):
   def __init__(self):
      self._cache = self._cache_ready = None
   def _check(self):
      if not self._cache_ready:
         self._cache_ready = True
         self._cache = self._fill()
      return self._cache
   def empty(self):
      return empty(self._check())
   def first(self):
      return first(self._check())
   def rest(self):
      return rest(self._check())
   def _simplify(self):
      return self._cache if self._cache_ready else self

def map(f, seq):
   seq = coerce_to_seq(seq)
   return null if seq is null else Map(f, seq)
class Map(Lazy):
   def __init__(self, f, seq):
      self._f, self._seq = f, seq
   def _fill(self):
      init = self._f(init, first(self._seq))
      return cons(self._f(first(self._seq)), map(self._f, rest(self._seq)))


def reduce(f, init, seq):
   seq = coerce_to_seq(seq)
   return null if seq is null else Reduce(f, init, seq)
class Reduce(Lazy):
   def __init__(self, f, init, seq):
      self._f, self._init, self._seq = f, init, seq
   def _fill(self):
      init = self._f(init, first(self._seq))
      return cons(init,
                  reduce(self._f, init, rest(self._seq)))

def iterable(g):
   if isinstance(g, Seq):
      return g
   return SeqIterable(g)
class SeqIterable(Lazy):
   def __init__(self, g):
      self._g = g
      super().__init__()
   def _fill(self):
      try:
         first = next(self._g)
         return cons(first, SeqIterable(self._g))
      except Exception as exc:
         breakpoint()


def each(seq):
   while not empty(ic(seq)):
      yield first(seq)
      seq = rest(seq)
