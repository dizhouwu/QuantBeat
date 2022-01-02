from typing import Iterable
import functools


def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x


# A bug in functools causes it to break if the wrapper is an instance method
def update_wrapper(wrapper, wrapped, *a, **ka):
    """
    https://github.com/bottlepy/bottle/blob/master/bottle.py
    """
    try:
        functools.update_wrapper(wrapper, wrapped, *a, **ka)
    except AttributeError:
        pass


class cached_property:
    """A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property."""

    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
