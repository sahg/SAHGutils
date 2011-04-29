__all__ = ['TRMM3B42RTFile', 'read3B42RT']

import sys
from gzip import GzipFile

import numpy as np

from numpy import ma

from arraytools import find_indices

def read3B42RT(fname):
    precip_scale_factor = 100.0
    rows = 480
    cols = 1440

    fp = open(fname, 'rb')
    data_string = fp.read()
    fp.close()

    precip = np.fromstring(data_string[2880:1385280], np.int16)
    precip = precip.byteswap()
    precip = np.asarray(precip, np.float32)
    precip /= precip_scale_factor
    precip = ma.masked_less_equal(precip, 0)
    precip = precip.reshape(rows, cols)

    return precip

class TRMM3B42RTFile:
    """Class for read operations on TRMM 3B42RT files.

    Example Usage:

    >>> from dataflow.trmm import TRMM3B42RTFile
    >>> current_file = TRMM3B42RTFile(file_name)
    >>> precip = current_file.precip()
    >>> print 'Array dimensions:', precip.shape
    >>> print 'Data max:', precip.max()
    >>> print 'Data min:', precip.min()
    >>> print 'Data mean:', precip.mean()
    >>> print 'Data std-dev:', precip.std()

    """
    def __init__(self, file_name):
        self.fname = file_name
        self.info = dict(cols=1440,
                         rows=480,
                         ll_lon=0.125,
                         ll_lat=-59.875,
                         dlon=0.25,
                         dlat=0.25,
                         grid_size=0.25)

    def precip(self, scaled=True, floats=True, masked=True):
        """Return the entire field of rainfall values.

        The data are returned as a 2D Numpy array.

        """
        precip_scale_factor = 100.0
        rows = 480 # The file headers lie about number of rows
        cols = 1440

        if self.fname.split('.')[-1] == 'gz':
            fp = GzipFile(self.fname)
        else: # assume decompressed binary file
            fp = open(self.fname, 'rb')
        data_string = fp.read()
        fp.close()

        precip = np.fromstring(data_string[2880:1385280], np.int16)
        if sys.byteorder == 'little':
            precip = precip.byteswap()
        if floats:
            precip = np.asarray(precip, np.float32)
        if scaled:
            precip /= precip_scale_factor
        if masked:
            precip = ma.masked_less(precip, 0)
        precip = precip.reshape(rows, cols)

        return precip

    def header(self, scaled=True, floats=True, masked=True):
        """Return the file header in a dictionary.

        """
        if self.fname.split('.')[-1] == 'gz':
            fp = GzipFile(self.fname)
        else: # assume decompressed binary file
            fp = open(self.fname, 'rb')
        data_string = fp.read()
        fp.close()

        hdr = {}
        for item in data_string[:2880].split():
            key, val = item.split('=')
            hdr[key] = val

        return hdr

    def point_values(self, lats, lons):
        """Get the rainfall value at one or more locations.

        A simple nearest neighbour algorithm is used with the returned value
        being the rainfall of the grid box containing the location(s).

        """
        ncols = self.info['cols']
        nrows = self.info['rows']
        lon0 = self.info['ll_lon']
        lat0 = self.info['ll_lat']
        dlon = self.info['dlon']
        dlat = self.info['dlat']

        row_indices, col_indices = find_indices(lats, lons, lat0, lon0,
                                                dlat, dlon, nrows, ncols)

        row_indices = np.asarray(row_indices)
        col_indices = np.asarray(col_indices)

        if row_indices.shape != () and col_indices.shape != ():# multiple points
            rindices = row_indices[(row_indices != -999)
                                   & (col_indices != -999)]
            cindices = col_indices[(row_indices != -999)
                                   & (col_indices != -999)]
        else:# scalar
            rindices = row_indices
            cindices = col_indices

        precip = self.precip()

        result = precip[rindices, cindices]

        return result

    def clip_precip(self, min_lat, max_lat, min_lon, max_lon):
        """Obtain a sub-region specified by a bounding box.

        A 2D masked array is returned. Only pixels with centres
        falling inside the bounding box are returned. If pixel centres
        fall exactly on the boundaries, these pixels are also
        included.

        """
        lon, lat = self._define_grid(min_lon, min_lat, max_lon, max_lat)

        rows = np.unique(lat).size
        cols = np.unique(lon).size

        result = self.point_values(lat, lon).reshape((rows, cols))
        
        return result

    def _define_grid(self, ll_lon, ll_lat, ur_lon, ur_lat):
        """Extract a sub-set of the TRMM 3B42RT grid."""
        cols = self.info['cols']
        rows = self.info['rows']
        x0 = self.info['ll_lon']
        y0 = self.info['ll_lat']
        cell_size = self.info['grid_size']

        # define the grid (pixel centre's)
        xt, yt = np.meshgrid(np.linspace(x0, x0 + (cols-1)*cell_size, num=cols),
                             np.linspace(y0 + (rows-1)*cell_size, y0, num=rows))

        xt = xt.flatten()
        yt = yt.flatten()

        # define points inside the specified domain
        lon = xt[(xt >= ll_lon) & (xt <= ur_lon) &
                  (yt >= ll_lat) & (yt <= ur_lat)]

        lat = yt[(xt >= ll_lon) & (xt <= ur_lon) &
                  (yt >= ll_lat) & (yt <= ur_lat)]

        return lon, lat

if __name__ == '__main__':
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.basemap import Basemap

    rain_dict = {'red':   ((0    , 1 , 1  ),
                        (0.35 , 0  , 0  ),
                        (0.66 , 1  , 1  ),
                        (0.89 , 1  , 1  ),
                        (1    , 0  , 0  )),
                'green': ((0    , 1 , 1  ),
                        (0.125, 0  , 0  ),
                        (0.375, 1  , 1  ),
                        (0.64 , 1  , 1  ),
                        (0.91 , 0  , 0  ),
                        (1    , 0  , 0  )),
                'blue':  ((0    , 1 , 1 ),
                        (0.11 , 1  , 1  ),
                        (0.34 , 1  , 1  ),
                        (0.65 ,0   , 0  ),
                        (1    , 0  , 0  ))}

    fname = 'data/3B42RT.2008072406.bin'
    fig_name = '3B42RT.png'

    current_file = TRMM3B42RTFile(fname)
    precip = current_file.precip()

    # define domain
    ll_lon = 0
    ll_lat = -60
    ur_lon = 360
    ur_lat = 60

    # create new figure
    fig = Figure()
    ax = fig.add_subplot(1,1,1)

    # make a plot on a map
    curr_map = Basemap(projection='cyl', llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                        urcrnrlon=ur_lon, urcrnrlat=ur_lat, resolution='l',
                        ax=ax, area_thresh=1000.)

    # draw country borders
    curr_map.drawcoastlines(linewidth=0.5)
    curr_map.drawcountries(linewidth=0.5)

    rain_cmap = LinearSegmentedColormap('rain_colormap', rain_dict, 256)

    im = curr_map.imshow(precip, cmap=rain_cmap, origin='upper',
                         interpolation='nearest', vmin=0, vmax=35)

    # setup colorbar axes and draw colorbar
    bbox = ax.get_position()
    l,b,w,h = bbox.bounds
    cax = fig.add_axes([l+w+0.025, b, 0.025, h],frameon=False)
    fig.colorbar(im, cax=cax)

    # draw parallels and meridians.
    circles = np.linspace(60, -60, 9)
    curr_map.drawparallels(circles, labels=[1,0,0,0])

    meridians = np.linspace(0, 360, 9)
    curr_map.drawmeridians(meridians,labels=[0,0,0,1])

    ax.set_title('TRMM 3B42RT Rainfall - 06:00 24/07/2008',
                 fontweight='bold')

    canvas = FigureCanvas(fig)
    canvas.print_figure(fig_name)

    lons = [28.35420,
            28.79889,
            28.29527,
            27.42864,
            26.58199,
            26.68224,
            28.61503,
            26.90879,
            30.48352,
            28.95819,
            29.55925,
            29.61425,
            29.06750,
            29.66667,
            26.23708,
            26.61900,
            27.29116]

    lats = [-25.60398,
            -25.70208,
            -28.16258,
            -27.20533,
            -27.15454,
            -27.30338,
            -27.03676,
            -27.17913,
            -26.56770,
            -26.99549,
            -24.30808,
            -24.46554,
            -24.62470,
            -23.85000,
            -26.22662,
            -26.48042,
            -25.72391]

    point_values = current_file.point_values(lats, lons)

    print point_values
