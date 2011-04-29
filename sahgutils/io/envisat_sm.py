"""Utilities for reading ENVISAT SM files.

This module contains some simple functions to make it easier
to read the data contained in the binary files produced by IPF TUWien.

Author: Scott Sinclair <scott.sinclair.za -at- gmail.com>

"""
import sys
from math import ceil

import numpy as np
from numpy import ma

class EnvisatFile:
    """Class for basic read operations on ENVISAT SM files.

    Example Usage:

    >>> from dataflow.envisat_sm import EnvisatFile
    >>> current_file = EnvisatFile(file_name)
    >>> data = current_file.get_data()
    >>> print 'Array dimensions:', data.shape
    >>> print 'Data max:', data.max()
    >>> print 'Data min:', data.min()
    >>> print 'Data mean:', data.mean()
    >>> print 'Data std-dev:', data.std()

    """
    def __init__(self, file_name, no_data=-9999):
        self.name = file_name
        self._read_headers()
        self.no_data = no_data

    def get_data(self, ll_lat=None, ll_lon=None, ur_lat=None, ur_lon=None):
        """Read the data into a masked 2D Numpy array.

        Both 'no data' and areas with poor surface characteristics are masked
        in the returned array. If ll_lat, ll_lon, ur_lat, ur_lon are specified
        then a masked data array is constructed to fill this region and the
        ENVISAT data is embedded in the correct location, otherwise only the
        ENVISAT data is returned.

        """
        bin_name = self.name + '.img'
        data = np.fromfile(bin_name, np.float32)
        if sys.byteorder == 'big':
            data = data.byteswap()

        nrows = int(self.info['lines'])
        ncols = int(self.info['samples'])

        data = data.reshape(nrows, ncols)

        if (ll_lat != None) and (ll_lon != None) \
           and (ur_lat != None) and (ur_lon != None):
            # embed data in large array
            dlon = float(self.info['map info'].split(',')[5].strip())
            dlat = float(self.info['map info'].split(',')[5].strip())
            lon0 = float(self.info['ul_lon'])
            lat0 = float(self.info['ul_lat'])

            big_nrows = int(ceil((ur_lat - ll_lat)/dlat))
            big_ncols = int(ceil((ur_lon - ll_lon)/dlon))

            big_data = np.ones((big_nrows, big_ncols))
            big_data *= -10000

            start_row = int(ceil((ur_lat - lat0)/dlat))
            start_col = int(ceil((lon0 - ll_lon)/dlon))

            big_data[start_row:start_row+nrows, start_col:start_col+ncols] = data
            data = ma.masked_less_equal(big_data, -9999)
        else:
            data = ma.masked_less_equal(data, -9999)

        return data

    def get_data_points(self):
        """Read the data into lists of lats, lons and data value.

        Pixels with 'no data' and poor surface characteristics are not returned.

        """
        bin_name = self.name + '.img'
        raw_data = np.fromfile(bin_name, np.float32)
        if sys.byteorder == 'big':
            raw_data = raw_data.byteswap()

        ncols = int(self.info['samples'])
        nrows = int(self.info['lines'])
        lon0 = float(self.info['ul_lon'])
        lat0 = float(self.info['ul_lat'])
        dlon = float(self.info['map info'].split(',')[5].strip())
        dlat = -float(self.info['map info'].split(',')[5].strip())

        lns = np.linspace(lon0, lon0 + (ncols*dlon), ncols)
        lts = np.linspace(lat0, lat0 + (nrows*dlat), nrows)

        lons = []
        lats = []
        for lat_val in lts:
            for lon_val in lns:
                lats.append(lat_val)
                lons.append(lon_val)

        lons = np.array(lons)
        lats = np.array(lats)

        data = raw_data[raw_data > -9999]
        lons = lons[raw_data > -9999]
        lats = lats[raw_data > -9999]

        return lats, lons, data

    def get_pixel(self, lats, lons):
        """Get the value at one or more pixels described by location.

        A simple nearest neighbour algorithm is used. If scalar values are
        input, the result is scalars.

        """
        Lats = np.asarray(lats)
        Lons = np.asarray(lons)
        ncols = int(self.info['samples'])
        nrows = int(self.info['lines'])
        lon0 = float(self.info['ul_lon'])
        lat0 = float(self.info['ul_lat'])
        dlon = float(self.info['map info'].split(',')[5].strip())
        dlat = -float(self.info['map info'].split(',')[5].strip())

        if Lats.shape != () and Lons.shape != ():
            # find the cells containing each data point
            col_indices = []
            for lon in Lons:
                col_indices.append(int(ceil((lon-lon0)/dlon) - 1))

            row_indices = []
            for lat in Lats:
                row_indices.append(int(ceil((lat-lat0)/dlat)) - 1)

            data = self.get_data()

            values = []
            for k in xrange(len(col_indices)):
                row = row_indices[k]
                col = col_indices[k]
                if (0 <= row < nrows) and (0 <= col < ncols):
                    values.append(data[row, col])
                else:
                    values.append(self.no_data)

        else:# scalar input
            # find the cells containing the data point
            col = int(ceil((lons-lon0)/dlon)) - 1
            row = int(ceil((lats-lat0)/dlat)) - 1

            data = self.get_data()

            if (0 <= row < nrows) and (0 <= col < ncols):
                values = data[row, col]
            else:
                values = self.no_data

        return values

    def get_area_mean(self, ul_lat, ul_lon, lr_lat, lr_lon):
        """Get the mean value over a rectangular region.

        Masked pixels are ignored in the calculation.

        """
        ncols = int(self.info['samples'])
        nrows = int(self.info['lines'])
        lon0 = float(self.info['ul_lon'])
        lat0 = float(self.info['ul_lat'])
        dlon = float(self.info['map info'].split(',')[5].strip())
        dlat = -float(self.info['map info'].split(',')[5].strip())

        # find the cells containing each data point
        start_col = int(ceil((ul_lon-lon0)/dlon)) - 1
        end_col = int(ceil((lr_lon-lon0)/dlon)) - 1

        start_row = int(ceil((ul_lat-lat0)/dlat)) - 1
        end_row = int(ceil((lr_lat-lat0)/dlat)) - 1

        if (0 <= start_row < nrows) and (0 <= end_row < nrows) \
        and (0 <= start_col < ncols) and (0 <= end_col < ncols):
            data = self.get_data()
            region = data[start_row:end_row, start_col:end_col]
            region = region.clip(0.0, 1.0)
            result = region.mean()

            # Handle the case where the whole region is masked
            if result.mask:
                result = self.no_data
        else:
            result = self.no_data

        return result

    def get_raw_data(self):
        """Read the data into a Numpy array.

        No masking or reshaping of the data is applied in this function.

        """
        bin_name = self.name + '.img'
        data = np.fromfile(bin_name, np.float32)
        if sys.byteorder == 'big':
            data = data.byteswap()

        return data

    def _read_headers(self):
        """Read the ascii header file describing the binary file

        The headers have the following format:

        ENVI description = {File Imported into ENVI.}
        Param. descr.    = 1 km Surface Soil Moisture at 20060102_201144
        samples          = 360
        lines            = 840
        bands            = 1
        header offset    = 0
        file type        = ENVI standard
        data type        = 4
        interleave       = bsq
        map info = {Geographic Lat/Lon, 0.5, 0.5, 32.000000000, -21.500000000, 0.004166667, 0.004166667, WGS-84, units=Degrees}
        x start          = 0
        y start          = 0
        ul_lat           = -21.500000000
        ul_lon           = 32.000000000

        """

        hdr_name = self.name + '.hdr'
        f = open(hdr_name, 'r')

        info_list = []
        for line in f:
            pair = line.split('=')
            key = pair[0].strip()
            value = pair[1].strip()
            info_list.append((key, value))

        f.close()

        self.info = dict(info_list)
