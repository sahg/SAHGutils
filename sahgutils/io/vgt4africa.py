"""Utilities for reading data files available from VGT4Africa.

This module contains tools for reading the data products provided by
the VGT4Africa project (http://www.vgt4africa.org). The data products
are distributed in HDF format via EUMETCast and the Python GDAL
bindings are used to access the data. Numpy is also required.

"""
import os
from zipfile import ZipFile

import numpy as np
from numpy import ma

try:
    from osgeo import gdal
    import osgeo.gdalconst as gdalc
except ImportError:
    import gdal
    import gdalconst as gdalc

from arraytools import Raster

def read_ndvi(ndvi_fname, min_lat=None, min_lon=None,
              max_lat=None, max_lon=None, masked=True):
    """Read VGT4Africa NDVI product.

    Read the NDVI data into a Numpy masked array, using the GDAL Python
    bindings.

    Parameters
    ----------
    ndvi_fname : string
        A string containing the name of a zipped archive containing the
        NDVI dataset and associated files.
    min_x : float
        The minimum x value of the required sub-region. Entire region is
        returned if None (default).
    min_y : float
        The minimum y value of the required sub-region. Entire region is
        returned if None (default).
    max_x : float
        The maximum x value of the required sub-region. Entire region is
        returned if None (default).
    max_y : float
        The maximum y value of the required sub-region. Entire region is
        returned if None (default).
    masked : bool
        Flag specifying whether to return the data as a MaskedArray (default)
        or a Raster object.

    Returns
    -------
    ndvi : {MaskedArray, Raster}
        A Numpy Masked Array object or Raster depending on the value of the
        `masked` parameter.

    """
    temp_fname = 'curr.hdf'

    archive = ZipFile(ndvi_fname)

    metadata = archive.read('0001/0001_LOG.TXT')

    key_val = []
    for item in metadata.split('\r\n'):
        splitta = item.split()
        if len(splitta) > 0:
            key, value = splitta[:2]
            key_val.append((key, value))

    metadata = dict(key_val)

    dx = float(metadata['MAP_PROJ_RESOLUTION'])
    dy = float(metadata['MAP_PROJ_RESOLUTION'])

    x0 = float(metadata['CARTO_LOWER_LEFT_X'])
    x0 += dx/2.0

    y0 = float(metadata['CARTO_LOWER_LEFT_Y'])
    y0 += dy/2.0

    # write a temporary HDF file
    fp = open(temp_fname, 'wb')
    fp.write(archive.read('0001/0001_NDV.HDF'))
    fp.close()

    archive.close()

    dataset = gdal.Open(temp_fname, gdalc.GA_ReadOnly)
    if dataset == None:
        os.remove(temp_fname)

        raise OSError, 'GDAL installation does not support HDF. ' \
              'Please rebuild with HDF support.'

    data = dataset.ReadAsArray()

    if (min_lat is not None
       and min_lon is not None
       and max_lat is not None
       and max_lon is not None):
        ndvi = Raster(data, x0, y0, dx, dy)
        ndvi = ndvi.subset(min_lon, min_lat, max_lon, max_lat)
    else:
        ndvi = data

    if masked:
        ndvi = ma.masked_equal(ndvi, 0) # mask out sea
        ndvi = 0.004*ndvi - 0.1 # convert uint8 to NDVI values
        ndvi = ndvi.clip(0, 0.8)
    else:
        # return a Raster object
        if not isinstance(ndvi, Raster):
            ndvi = Raster(data, x0, y0, dx, dy)

    os.remove(temp_fname)

    return ndvi

def plot_ndvi(hdf_fname, fig_name,
              min_lat, min_lon, max_lat, max_lon, title='NDVI plot'):
    """Produce a plot of the NDVI data in file `hdf_fname`."""

    import matplotlib.pyplot as plt
    from matplotlib import cm
    from mpl_toolkits.basemap import Basemap

    ndvi = read_ndvi(hdf_fname, min_lat, min_lon, max_lat, max_lon)

    print 'Data obtained'
    print type(ndvi)

    fig = plt.figure()

    ax = fig.add_subplot(111)

    curr_map = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat,
                       llcrnrlon=min_lon, urcrnrlon=max_lon, resolution='l')
    curr_map.drawcoastlines(linewidth=1.5)
    curr_map.drawcountries(linewidth=1.5)
    curr_map.drawparallels(np.arange(-90.,91.,2.), labels=[1, 0, 0, 0])
    curr_map.drawmeridians(np.arange(-180.,181.,2.), labels=[1, 0, 0, 1])

    im = curr_map.imshow(ndvi, cmap=cm.BrBG,
                         origin='upper', interpolation='nearest')
    cbar = fig.colorbar(im, ticks=[0, 0.4, 0.8])

    cbar.set_label('NDVI')
    cbar.ax.set_yticklabels(['< 0', '0.4', '> 0.8'])

    ax.set_title(title, fontsize=16, fontweight='bold')

    fig.savefig(fig_name)
