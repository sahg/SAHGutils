""" A collection of tools for manipulating Numpy arrays

This module contains a number of convenience routines for
common manipulations of data stored in 1-D and 2-D arrays.

"""
from math import floor

import numpy as np

def find_indices(lats, lons, lat0, lon0, dlat, dlon, nrows, ncols):
    """Find row and column indices into a 2D array.
    
    The location of each element in the 2D array is specified by the latitude 
    and longitude of the *centre* of the cell at the lower left corner of the 
    array (lat0, lon0) and the incremental change in latitude and longitude 
    between each element 'dlat' and 'dlon'. The number of rows and columns in 
    the array is given by nrows and ncols respectively.
    
    Returns: Lists of row and column indices, indices have a value of -999 if 
             the input location is outside of the defined data region.

    """
    Lats = np.asarray(lats)
    Lons = np.asarray(lons)
    min_lat = lat0 - 0.5*dlat
    max_lat = min_lat + nrows*dlat
    min_lon = lon0 - 0.5*dlon
    max_lon = min_lon + ncols*dlon

    if Lats.shape != () and Lons.shape != ():# multiple points
        row_indices = []
        for lat in lats:
            if lat < min_lat or max_lat < lat:# outside region
                row = -999
            elif (max_lat - dlat) <= lat <= max_lat:# first row
                row = 0
            elif min_lat <= lat <= (min_lat + dlat):# last row
                row = nrows-1
            else:# everywhere else
                diff = lat - min_lat
                row = int(floor(nrows - diff/dlat))
                    
            row_indices.append(row)
            
        col_indices = []
        for lon in lons:
            if lon < min_lon or max_lon < lon:# outside region
                col = -999
            elif min_lon <= lon <= (min_lon + dlon):# first column
                col = 0
            elif (max_lon - dlon) <= lon <= max_lon:# last column
                col = ncols-1
            else:# everywhere else
                diff = lon - min_lon
                col = int(floor(diff/dlon))
                    
            col_indices.append(col)
    else:# scalar input
        if lats < min_lat or max_lat < lats:# outside region
            row = -999
        elif (max_lat - dlat) <= lats <= max_lat:# first row
            row = 0
        elif min_lat <= lats <= (min_lat + dlat):# last row
            row = nrows-1
        else:# everywhere else
            diff = lats - min_lat
            row = int(floor(nrows - diff/dlat))
                
        row_indices = row
            
        if lons < min_lon or max_lon < lons:# outside region
            col = -999
        elif min_lon <= lons <= (min_lon + dlon):# first column
            col = 0
        elif (max_lon - dlon) <= lons <= max_lon:# last column
            col = ncols-1
        else:# everywhere else
            diff = lons - min_lon
            col = int(floor(diff/dlon))
                
        col_indices = col

    return row_indices, col_indices

def embed(arr, shape, pos='centre'):
    """ Embed a 2D array in a larger one.

    This function returns a 2D array embeded in a larger one with
    size determined by the shape parameter. The purpose is for
    border padding an input array with zeros. The embedded array
    is centred in the larger array.

    """
    newsize = np.asarray(shape)
    currsize = np.array(arr.shape)
    startind = (newsize - currsize) / 2
    endind = startind + currsize

    sr = startind[0]
    sc = startind[1]
    er = endind[0]
    ec = endind[1]

    result = np.zeros(shape)
    result[sr:er, sc:ec] = arr
    
    return result
    
def crop(arr, shape, pos='centre'):
    """ Crop a 2D array from a larger one.

    This function returns a 2D array cropped from the centre of
    the larger input array.

    """
    newsize = np.asarray(shape)
    currsize = np.array(arr.shape)
    startind = (currsize - newsize) / 2
    endind = startind + newsize

    sr = startind[0]
    sc = startind[1]
    er = endind[0]
    ec = endind[1]

    return arr[sr:er, sc:ec]

class Raster(np.ndarray):
#class Raster(np.ma.MaskedArray): # TO DO: Consider this at some point..
    """
    Raster(data, x0, y0, dx, dy, origin='Lower')
    
    This class attempts to unify the handling of remote sensing data and the
    typical operations performed on it.  Many data formats are not natively
    ingested by a GIS and are therefore difficult to process using these tools.
    
    Raster is a subclass of a Numpy ndarray containing additional 
    attributes, which describe the data grid.  The origin of the grid is
    defined by the point (`x0`, `y0`) in the units of the map projection 
    and coordinate system in which the data are defined.
    
    Parameters
    ----------
    data : array_like
        A 2D array containing the raster data.
    x0 : float
        The x origin of the data grid in the units of the map projection and
        coordinate system.
    y0 : float
        The y origin of the data grid in the units of the map projection and
        coordinate system.
    dx : float
        The regular grid spacing along the x axis.  Irregular grids are not
        supported.
    dy : float
        The regular grid spacing along the y axis.  Irregular grids are not
        supported.
    origin : {'Lower', 'Upper'}
        A string describing where (`x0`, `y0`) is located.  The default value
        of `Lower` means that the grid origin is at the centre of the lower
        left grid cell.  The only accepted alternative value is `Upper`, which
        defines the origin as the top left.
    
    Attributes
    ----------
    rows : int
        The number of rows in the data grid.
    cols : int
        The number of columns in the data grid.
    x0 : float
        The x origin of the data grid in the units of the map projection and
        coordinate system.
    y0 : float
        The y origin of the data grid in the units of the map projection and
        coordinate system.
    dx : float
        The regular grid spacing along the x axis.  Irregular grids are not
        supported.
    dy : float
        The regular grid spacing along the y axis.  Irregular grids are not
        supported.
    origin : {'Lower', 'Upper'}
        A string describing where (`x0`, `y0`) is located.  The default value
        of `Lower` means that the grid origin is at the centre of the lower
        left grid cell.  The only accepted alternative value is `Upper`, which
        defines the origin as the top left.
        
    Methods
    -------
    subset(min_x, min_y, max_x, max_y)
        Extract a sub-region from the Raster.
    
    """
    def __new__(cls, data, x0, y0, dx, dy, origin='Lower'):
        if origin != 'Lower':
            raise NotImplementedError("'%s' is not a suitable origin" % origin)
        
        # Input array is an already formed ndarray instance
        # or array_like object.
        # We first cast to be our class type
        obj = np.asarray(data).view(cls)
        
        # add the new attribute to the created instance
        obj.rows, obj.cols = obj.shape
        obj.dx = dx
        obj.dy = dy
        obj.x0 = x0
        obj.y0 = y0
        obj.origin = origin
        
        # Finally, we must return the newly created object:
        return obj

#    # TO DO:
#    # Slicing of raster objects needs to be handled carefully..
#    def __array_finalize__(self, obj):
#        err = 'Slicing of Raster objects not supported, ' \
#        'please use the subset() method instead.'
#        raise NotImplementedError(err)
#        # reset the attribute from passed original object
#        self.rows, self.cols = self.shape 
#        self.dx = getattr(obj, 'dx', None)
#        self.dy = getattr(obj, 'dy', None)
#        self.x0 = getattr(obj, 'x0', None)
#        self.y0 = getattr(obj, 'y0', None)
#        self.origin = getattr(obj, 'origin', None)
#        # We do not need to return anything
        
    def subset(self, min_x, min_y, max_x, max_y):
        """Extract a sub-region from the Raster.
    
        Crop a sub-region from the Raster. A Raster object containing a copy
        of the relevant portion of data is returned and its attributes reflect
        the new origin and shape of the data.  No resampling is done and the
        resulting Raster will only match the requested region within a
        tolerance defined by the grid spacing (`dx` and `dy`).
        
        Parameters
        ----------
        min_x : float
            The minimum x value of the required sub-region.
        min_y : float
            The minimum y value of the required sub-region.
        max_x : float
            The maximum x value of the required sub-region.
        max_y : float
            The maximum y value of the required sub-region.
            
        Returns
        -------
        result : Raster
            A sub-region of the original Raster.
    
        """
        Y = [max_y, min_y]
        X = [min_x, max_x]
        row_indices, col_indices = find_indices(Y, X, 
                                                self.y0, self.x0, 
                                                self.dy, self.dx, 
                                                self.rows, self.cols)
        min_row, max_row = np.asarray(row_indices)
        min_col, max_col = np.asarray(col_indices)
        
        # TO DO: Assign correct values to x0, y0 when origin='Upper'
        # is implemented..
        if self.origin == 'Lower':
            new_x0 = self.x0 + min_col*self.dx
            new_y0 = self.y0 + (self.rows - 1 - max_row)*self.dy
        
        result = Raster(self[min_row:max_row, min_col:max_col], 
                        x0=new_x0, 
                        y0=new_y0, 
                        dx=self.dx, 
                        dy=self.dy,
                        origin=self.origin)
    
        return result

    def sample(self, x, y):
        """Sample the Raster at multiple locations.
    
        Sample the Raster at multiple scattered locations.  Sampling is done
        using a nearest neighbour approach and no interpolation.  The values
        of the Raster grid cells whose centres are closest to the locations
        specifed by `x` and `y` are returned.
        
        Parameters
        ----------
        x : array_like
            An array of x values for each location.
        y : array_like
            An array of Y values for each location.
            
        Returns
        -------
        result : ndarray
            An array of values sampled from the Raster.
    
        """
        if self.origin == 'Lower':
            row_indices, col_indices = find_indices(y, x, 
                                                    self.y0, self.x0, 
                                                    self.dy, self.dx, 
                                                    self.rows, self.cols)
        
        row_indices = np.asarray(row_indices)
        col_indices = np.asarray(col_indices)
    
        mask = (row_indices != -999) & (col_indices != -999)
    
        row_indices = row_indices[mask]
        col_indices = col_indices[mask]
        
        result = np.ones(len(x), dtype=self.dtype)
        result *= -999
        result[mask] = self[row_indices, col_indices]
        
        return result
