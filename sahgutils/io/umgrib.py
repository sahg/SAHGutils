"""Utilities for reading and plotting GRIB1 files.

This module contains some simple functions to make it easier
to read and plot the data from GRIB(version 1) files produced
by SAWS Unified Model. The module relies on Wesley Ebisuzaki's
wgrib programme being somewhere on your systems path. If you
don't have wgrib it can be obtained from:

http://www.cpc.ncep.noaa.gov/products/wesley/wgrib.html

"""

import os
import sys

import numpy as np

def execute(command):
    """Execute a system command passed as a string."""
    
    print 'Running:', command
    os.system(command)
    print 'Done----------------\n'
    
def read_bin_data(fname):
    """Read data from a binary file into an array.
    
    Read the data from a binary file created by wgrib into
    a Numpy array. This assumes that wgrib has output the data
    in float format and seems to work for the UM outputs that
    are being sent to us by SAWS. The first and last values
    read from the file are trimmed since they are superflous.

    """
    
    f = open(fname, "rb")
    raw = f.read()
    f.close()
    data = np.fromstring(raw, 'f')
    data = data[1:-1] # trim invalid values - FORTRAN header
    if sys.byteorder == 'big':
        data = data.byteswap()

    return data

def read(grb_name, record=1, rows=401, cols=601):
    """Read the data field from a grib file into an array.

    This function uses wgrib to write and then read the GRIB1
    data to an intermediate binary format, which is later
    deleted. It is currently very specific to the GRIB1 data
    files produced by the UM.

    """
    
    bin_name = grb_name[0:-5] + '.bin'

    # note that spaces are N.B.
##    exec_str = 'wgrib ' + grb_name + ' -d ' + record + ' -bin -o ' + bin_name
    exec_str = 'wgrib %s -v -d %d -bin -o %s' % (grb_name, record, bin_name)

    execute(exec_str)
    a = read_bin_data(bin_name)
    os.remove(bin_name)

    a = a.reshape(rows, cols)
    a = np.flipud(a)

    return a

def plot(grb_name, fig_name, title='GRIB Plot', record=1, rows=401, cols=601):
    """Create a quick and dirty plot of the data in a GRIB1 file."""
    import pylab as pl
    
    a = read(grb_name, record, rows, cols)
    
    pl.imshow(a, origin='upper', interpolation='nearest')
##    pl.imshow(np.flipud(a), origin='upper', interpolation='nearest')
    pl.colorbar()
    pl.title(title)
    pl.savefig(fig_name)
    pl.close()

