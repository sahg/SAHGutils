import contextlib

import numpy as np
import numpy.core.arrayprint as arrayprint

# Context manager idea and code from StackOverflow user unutbu
# (Thanks!!)
# http://stackoverflow.com/questions/2891790/pretty-printing-of-numpy-array
@contextlib.contextmanager
def printoptions(strip_zeros=True, **kwargs):
    """Context manager to apply Numpy printoptions locally.

    Example usage:
    >>> x = np.array([0.078, 0.480, 0.413, 0.830, 0.776])
    >>> with printoptions(precision=3, suppress=True, strip_zeros=False):
            print(x)

    """
    origcall = arrayprint.FloatFormat.__call__
    def __call__(self, x, strip_zeros=strip_zeros):
        return origcall.__call__(self, x, strip_zeros)
    arrayprint.FloatFormat.__call__ = __call__
    original = np.get_printoptions()
    np.set_printoptions(**kwargs)
    yield
    np.set_printoptions(**original)
    arrayprint.FloatFormat.__call__ = origcall
