"""Provides convenience utilities for assorted data files.

This package provides a means of organizing the code developed
at UKZN for handling the dataflow and processing of information
for the WRC funded research project K5-1683 "Soil Moisture from
Space".

The interface isn't stable yet so be prepared to update your code
on a regular basis...

"""
from trmm import *

__all__ = filter(lambda s:not s.startswith('_'),dir())
