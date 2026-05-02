# Inspired by Clojure

from typing import (
    Any,
    Optional,
    Union,
    List,
    Tuple,
    Dict,
    Iterable,
    Mapping,
    Callable,
    Type,
    Literal,
    IO,
    NoReturn,
    Self,
)
from contextlib import contextmanager
from abc import ABC, abstractmethod
from numbers import Number
from collections.abc import Iterable, Iterator
from icecream import ic

ic.configureOutput(includeContext=True)


class SeqError(Exception):
    pass


class Seq(ABC):
    def empty(self) -> bool:
        return False

    def first(self) -> Any | NoReturn:
        raise SeqError()

    def rest(self) -> Self | NoReturn:
        raise SeqError()

    def __repr__(self):
        return f"sq.{type(self).__qualname__}(...)"

    def __iter__(self):
        "Returns a Python iterator."
        return SeqIterator(self)

    def length(self):
        return -1


class EmptySeq(Seq):
    "The empty Seq, an Iterable and Iterator of nothing."

    def empty(self) -> bool:
        return True

    def length(self):
        return 0

    def __repr__(self):
        return f"sq.Empty"

    def __iter__(self):
        return iter(())

    def __next__(self, *default):
        if default:
            return default[0]
        raise StopIteration("next(EmptySeq)")


Empty = EmptySeq()


def seq(x: None = None):
    "Returns a seq from a Python Iterable or Iterator."
    if x is None:
        return Empty
    if isinstance(x, Seq):
        return x
    if is_sizeable(x):
        return SizeableSeq(x, 0) if len(x) else Empty
    if is_iterator(x):
        return IteratorSeq(x)
    if is_iterable(x):
        return IteratorSeq(iter(x))
    raise SeqError(f"seq : {type(x)!r}")


def empty(x) -> Any | NoReturn:
    if isinstance(x, Seq):
        return x.empty()
    # if is_sizeable(x):
    #    return not len(x)
    raise SeqError(f"empty : {type(x)!r}")


def first(x) -> Any | NoReturn:
    if isinstance(x, Seq):
        return x.first()
    # if is_sizeable(x):
    #    return x[0]
    raise SeqError(f"first : {type(x)!r}")


def rest(x) -> Any | NoReturn:
    if isinstance(x, Seq):
        return x.rest()
    # if is_sizeable(x):
    #    return SizeableSeq(x, 1)
    raise SeqError(f"rest : {type(x)!r}")


####################################################


def length(x) -> int:
    i = 0
    while not empty(x):
        x = rest(x)
        i += 1
    return i


def doall(s):
    head = s = seq(s)
    while not empty(s):
        s = rest(s)
    first(head)
    return head


@contextmanager
def doseq(s):
    while not empty(s):
        ic(first(s))
        yield first(s)
        s = rest(s)


####################################################


def concat2(a, b):
    a, b = seq(a), seq(b)
    if empty(a) and empty(b):
        return Empty
    elif empty(b):
        return a
    return ConcatSeq(a, b)


def concat(a, *seqs):
    for s in seqs:
        a = concat2(a, s)
    return a


class ConcatSeq(Seq):
    def __init__(self, a, b):
        self._a, self._b = a, b

    def first(self):
        return first(self._a)

    def rest(self):
        return concat2(rest(self._a), self._b)

    def length(self):
        return length(self._a) + length(self._b)


####################################################

# def simplify(seq):
#    if seq.empty():
#       return Empty
#    return seq


def cons(first, rest):
    return Cons(first, seq(rest))


def cons_iter(itr):
    head = tail = Cons(Empty, Empty)
    for x in itr:
        tail._rest = Cons(x, Empty)
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

    # def length(self):
    #    return 1 + length(self._b)


####################################################


class Lazy(Seq):
    def __init__(self):
        self._cache = self._cache_ready = None

    def empty(self):
        return empty(self._fill())

    def first(self):
        return first(self._fill())

    def rest(self):
        return rest(self._fill())

    def _fill(self):
        if self._cache_ready:
            return self._cache
        self._cache, self._cache_ready = self._realize(), True
        return self._cache

    def length(self):
        return length(self._fill())

    @abstractmethod
    def _realize(self):
        pass


####################################################
# Python iterable compatibility


class SeqIterator:
    "Provides a Python iterator over a Seq."

    def __init__(self, s):
        self._s = s

    def __next__(self, *default):
        if empty(self._s):
            if default:
                return default[0]
            raise StopIteration()
        val = first(self._s)
        self._s = rest(self._s)
        return val


class SizeableSeq(Seq):
    def __init__(self, x, i):
        self._x, self._i = x, i

    def empty(self):
        return self._i >= len(self._x)

    def first(self):
        return self._x[self._i]

    def rest(self):
        if self._i + 1 >= len(self._x):
            return Empty
        return SizeableSeq(self._x, self._i + 1)

    # def length(self):
    #    return len(self._x) - self._i


class IteratorSeq(Lazy):
    "Provides a Seq over a Python iterator."

    def __init__(self, itr):
        super().__init__()
        self._itr = itr

    def empty(self):
        return True if self._itr is None else super().empty()

    def rest(self):
        return Empty if self._itr is None else super().rest()

    def _realize(self):
        try:
            val = next(self._itr)
            ic(val)
            return cons(val, IteratorSeq(self._itr))
        except StopIteration:
            self._itr = None
        return self


####################################################


def map(f, s):
    s = seq(s)
    return Empty if empty(s) else Map(f, s)


class Map(Lazy):
    def __init__(self, *f_s):
        self._cache = f_s
        self._cache_ready = None

    def _realize(self):
        f, s = self._cache
        return cons(f(first(s)), map(f, rest(s)))


####################################################


def reduce(f, init, s):
    s = seq(s)
    return Empty if empty(s) else Reduce(f, init, s)


class Reduce(Lazy):
    def __init__(self, *f_init_s):
        self._cache = f_init_s
        self._cache_ready = None

    def _realize(self):
        f, init, s = self._cache
        return cons(f(init, first(s)), reduce(f, init, rest(s)))


####################################################


def is_sizeable(x):
    return isinstance(x, (tuple, list, set))


def is_iterable(x):
    return isinstance(x, Iterable) or responds_to_iter(x)


def is_iterator(x):
    return isinstance(x, Iterator) or responds_to_next(x)


def responds_to_iter(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False


def responds_to_next(x):
    try:
        next(x, None)
        return True
    except TypeError:
        return False


####################################################


def identity(x):
    ic(x)
    return x


cl = cons_iter((1, 2, 3))
cl
breakpoint()
tuple(doall(cl))
itr = seq((1, 2, 3))
itr
