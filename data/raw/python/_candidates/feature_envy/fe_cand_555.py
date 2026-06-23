def _decorate_fun(self, fun):
    """Decorate function fun"""

    msg = "Function %s is deprecated" % fun.__name__
    if self.extra:
        msg += "; %s" % self.extra

    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        warnings.warn(msg, category=FutureWarning)
        return fun(*args, **kwargs)

    # Add a reference to the wrapped function so that we can introspect
    # on function arguments in Python 2 (already works in Python 3)
    wrapped.__wrapped__ = fun

    return wrapped
