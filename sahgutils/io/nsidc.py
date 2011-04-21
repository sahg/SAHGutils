"""Utilities for reading data files available from NSIDC.

This module contains functions for reading the data products provided by
the National Snow and Ice Data Center (http://nsidc.org). The data products
are distributed in HDF-EOS format and the Python GDAL bindings are used to
access the data. Numpy is also required.

Author: Scott Sinclair <scott.sinclair.za -at- gmail.com>

"""
import numpy as np
from numpy import ma

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
except ImportError:
    import gdal
    from gdalconst import *

def read_ae_land3(hdf_fname, dir='asc', field='Soil_Moisture'):
    """Read AMSR-E level 3 land products.

    Input parameters:
        - hdf_fname is a string containing the name of an HDF-EOS file
        - dir is a string representing the direction of the overpass
          required. 'asc' for ascending and 'desc' for descending.
        - field is a string defining the name of a sub-dataset in the
          HDF-EOS file (default 'Soil_Moisture')

    Output:
        - A masked Numpy array containing the data field. Data in the array
          are divided by a factor of 1000 as this yields soil moisture values
          in g/cm^3.

    """
    hdf = gdal.Open(hdf_fname)

    sdsdict = hdf.GetMetadata('SUBDATASETS')

    sdslist =[sdsdict[k] for k in sdsdict.keys() if '_NAME' in k]

    if dir == 'asc':
        field_tag = 'A_' + field
    elif dir == 'desc':
        field_tag = 'D_' + field
    else:
        raise ValueError, 'Invalid parameter passed for dir: %s' % (dir)

    name = [k for k in sdslist if field_tag in k][0]
    sds = gdal.Open(name)

    data = np.asarray(sds.ReadAsArray(), np.float32)
    data = ma.masked_values(data, -9999)
    data = ma.masked_values(data, 9999)
    data /= 1000.0 # Only necessary for Soil Moisture

    return data
