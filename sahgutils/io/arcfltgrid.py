"""Utilities for reading and plotting ArcGIS binary files.

This module contains some simple functions to make it easier
to read and plot the data contained in the binary grid files
produced by ArcGIS.

"""
import sys
import numpy as np
from numpy import ma


def read_bin(fname):
    """Read data from a ArcGIS binary file into an array.
    
    Read the data from a binary file created by ArcGIS into
    a Numpy array. The file is expected to be in binary format
    with floating point precision. e.g. ".flt" extension.

    """
    
    f = open(fname, "rb")
    raw = f.read()
    f.close()
    data = np.fromstring(raw, 'f')
    if sys.byteorder == 'big':
        data = data.byteswap()

    return data

def read(bingrid_name):
    """Read the data field and headers from an ArcGIS binary grid

    This function reads the header and data from the ArcGIS binary
    data files produced by the "Raster to Float" tool in ArcGIS 9.1

    """

    li_headers=read_headers(bingrid_name)

    rows = li_headers[1] # fixed for UM grid
    cols = li_headers[0] # fixed for UM grid
    
    bin_name = bingrid_name + '.flt'

    a = read_bin(bin_name)

    a = a.reshape(rows, cols)

    return a, li_headers

def read_headers(bingrid_name):
    """Read the ascii headers of the ArcGIS binary grid file

    The headers have the following format:
    
    ncols         62
    nrows         121
    xllcorner     -288595.47161281
    yllcorner     -3158065.5722693
    cellsize      1000
    NODATA_value  -9999
    byteorder     LSBFIRST
    """

    hdr_name = bingrid_name + '.hdr'
    f=open(hdr_name,'r')
    tab_read=f.readlines()
    f.close()

    li_headers=[]
    i=-1
    for line in tab_read:
        i=i+1
        donnees=line.split()
        if i<6:
            li_headers.append(float(donnees[1]))
        else:
            li_headers.append(donnees[1])
            
    return li_headers

def plot(bin_name, fig_name, title='Raster Plot'):
    """Create a plot of the data in an ArcGIS binary file."""
    import pylab as pl
    
    a, headers = read(bin_name)
    
    a_mask = ma.masked_where(a < 0, a)
    pl.imshow(a_mask, interpolation='nearest')
    pl.colorbar()
    pl.title(title)
    pl.savefig(fig_name)
    pl.close()

if __name__ == '__main__':
    plot('lieb_dem', 'lieb_dem.png', 'Liebenbergsvlei DEM')
    plot('saws_elev_spline', 'saws_elev_spline.png')

    
