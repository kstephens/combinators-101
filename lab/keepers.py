def defcombinator(f):
   def named(*args, **kwargs):
   return f


@combinator
def c(f):
   def g(*args):
      print(repr(args))
      return f(*args)
   return g


def format_args(name, args, kwargs):
    return f"{name}(" + ', '.join([repr(x) for x in args] + [f"{k!r}={v!r}" for k, v in kwargs.items()]) + ")"
