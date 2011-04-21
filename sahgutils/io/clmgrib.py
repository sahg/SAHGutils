"""Utilities for reading and plotting EUMETSAT Cloud Mask data.

This module contains some simple functions to make it easier
to read and plot the Meteosat-8 cloud mask produced by EUMETSAT.
The data are provied in GRIB2 files and the module currently
relies on Wesley Ebisuzaki's wgrib2 programme being somewhere
on your systems path. If you don't have wgrib2 it can be
obtained from:

http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/

"""

import os
import sys

import numpy as np
from numpy import ma
from scipy import io

import pylab as pl

def execute(command):
    """Execute a system command passed as a string."""
    
    print 'Running:', command
    os.system(command)
    print 'Done----------------\n'
    
def read_bin_data(fname):
    """Read data from a floating point binary file into an array.
    
    Read the data from a binary file created by wgrib2 into
    a Numpy array. This assumes that wgrib2 has output the data
    in 32bit floating point format and seems to work for the
    cloud mask data that are being sent via EumetCast and
    processed by David Taylors MDM software. The binary file
    is assumed to have no FORTRAN headers.

    """

    data = np.fromfile(fname, dtype=np.float32)    
##    data = data[1:-1] # trim invalid values if FORTRAN headers are present

    if sys.byteorder == 'big':#assumes that the data was written in little endian format
        data = data.byteswap()

    return data

def read(grb_name):
    """Read the cloud mask data from a grib file into an array.

    This function uses wgrib2 to write and then read the cloud mask
    data via an intermediate binary file, which is later
    deleted. The regions flagged as no data are masked. Although the
    data are in floating point three integer numbers define the mask
    as follows:

    Value | Class
      0   | Cloud free ocean or water body
      1   | Cloud free land surface
      2   | Cloud
      3   | Space/No data

    """
    
    rows = 3712 # fixed for MPE grid
    cols = 3712 # fixed for MPE grid

    bin_name = grb_name[0:-4] + '.bin'

    exec_str = 'wgrib2 -no_f77 ' + '-bin ' + bin_name + ' ' + grb_name # spaces are N.B.

    execute(exec_str)
    a = read_bin_data(bin_name)
    os.remove(bin_name)

    a = a.reshape(rows, cols)

    # data in grib file are oriented EW:SN
    # need to check that this is correct, the plots look fine...
    a = np.fliplr(a)
##    a = np.flipud(a)

    # mask no-data regions
    a = ma.masked_values(a, 3)

    return a

def write_arcgis_fltfile(grb_name):
    """Write the cloud mask data to a binary file suitable for ArcGIS.

    This function uses wgrib2 to write and then read the cloud mask
    data via an intermediate binary file, which is later
    deleted. The data is properly oriented and written to a binary
    file as 32-bit floats with the extension '.flt'. A suitable header
    is also written with the extension '.hdr'. The file may then be
    imported into ArcGIS.

    Although the data are in floating point three integer numbers
    define the mask as follows:

    Value | Class
      0   | Cloud free ocean or water body
      1   | Cloud free land surface
      2   | Cloud
      3   | Space/No data

    """
    
    rows = 3712 # fixed for MPE grid
    cols = 3712 # fixed for MPE grid

    bin_name = grb_name[0:-4] + '.bin'
    flt_name = grb_name[0:-4] + '.flt'
    hdr_name = grb_name[0:-4] + '.hdr'

    exec_str = 'wgrib2 -no_f77 ' + '-bin ' + bin_name + ' ' + grb_name # spaces are N.B.

    execute(exec_str)
    a = read_bin_data(bin_name)
    os.remove(bin_name)

    a = a.reshape(rows, cols)

    # data in grib file are oriented EW:SN
    # need to check that this is correct, the plots look fine...
    a = np.fliplr(a)
##    a = np.flipud(a)

    f = open(flt_name, 'wb')    
    io.fwrite(f, a.size, a, 'f')
    f.close()

    f = open(hdr_name, 'w')
    hdr_string = """ncols         3712
nrows         3712
xllcenter     -5565000
yllcenter     -5565000
cellsize      3000
NODATA_value  3
byteorder     LSBFIRST"""
    f.write(hdr_string)
    f.close()    

def plot(grb_name, fig_name, title='GRIB Plot'):
    """Create a plot of the data in a GRIB2 file."""
    
    a = read(grb_name)

    pl.clf()
    pl.imshow(a, interpolation='nearest', origin='upper')
    pl.colorbar()
    pl.title(title)
    pl.savefig(fig_name)
    pl.close()

