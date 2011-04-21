"""Utilities for reading data files from EUMETSAT's METOP satellite.

The Python interface to the eugene software available from EUMETSAT,
available from:

http://www.eumetsat.int/Home/Main/Access_to_Data/User_Support/SP_1117714787347#eugene

is used to access the data. Therefore this module will not work if the
software has not been installed on your system. Numpy is also
required.

"""
import os
from bz2 import BZ2File

import numpy as np

import eugene
eugene.disable_nav_cache(True)
eugene.set_default_baseline("v2l")

def read_ascat_soil_moisture(eps_fname, min_lat=None,
                             min_lon=None, max_lat=None,
                             max_lon=None, masked=True):
    """
    Read ASCAT level 2 soil moisture estimates.
    
    Parameters
    ----------
    eps_fname : string
        The name of a 25km resolution ASCAT level 2 soil moisture
        file. The format should be native EPS and bzip2 compressed
        files are supported.
    min_lat : scalar, optional
        The minimum latitude of the region within which the estimates
        are considered valid.
    min_lon : scalar, optional
        The minimum longitude of the region within which the estimates
        are considered valid.
    max_lat : scalar, optional
        The maximum latitude of the region within which the estimates
        are considered valid.
    max_lon : scalar, optional
        The maximum longitude of the region within which the estimates
        are considered valid.
    masked : bool, optional
        If True, then invalid data is ignored.
        
    Returns
    -------
    lons : ndarray
        A 1D NumPy array of longitude values.
    lats : ndarray
        A 1D NumPy array of latitude values.
    sm : ndarray
        A 1D NumPy array of surface soil moisture estimates.
    
    """
    temp_file = False
    
    if eps_fname[-3:] == 'bz2': # compressed file
        fname = eps_fname[:-4]
        
        fp = BZ2File(eps_fname)
        tmp = file(fname, 'wb')
        tmp.write(fp.read())
        fp.close()
        tmp.close()
        
        temp_file = True
        
    else: # assume uncompressed file
        fname = eps_fname
            
    eps_file = eugene.Product(fname)
    if masked:
        eugene.ignore_invalid_values(True)
        
    lons = np.array(eps_file.get("mdr-1b-25km[].LONGITUDE"))
    lats = np.array(eps_file.get("mdr-1b-25km[].LATITUDE"))
    data = np.array(eps_file.get("mdr-1b-25km[].SOIL_MOISTURE"))

    if (min_lat != None) & (max_lat != None) & \
       (min_lon != None) & (max_lon != None):
        
        condition = (min_lon <= lons) & (lons <= max_lon) \
                    & (min_lat <= lats) & (lats <= max_lat) \
                    & (0 <= data) & (data <= 100)
    else:
        
        condition = (0 <= data) & (data <= 100)
        
    lons = lons[condition].ravel()
    lats = lats[condition].ravel()
    sm = data[condition].ravel()

    del eps_file # hope to resolve the memory leak
    
    if temp_file:
        os.remove(fname)
    
    return lons, lats, sm

def read_ascat_sm_params(eps_fname, min_lat=None,
                         min_lon=None, max_lat=None,
                         max_lon=None, masked=True):
    """
    Read ASCAT level 2 soil moisture estimates.
    
    Parameters
    ----------
    eps_fname : string
        The name of a 25km resolution ASCAT level 2 soil moisture
        file. The format should be native EPS and bzip2 compressed
        files are supported.
    min_lat : scalar, optional
        The minimum latitude of the region within which the estimates
        are considered valid.
    min_lon : scalar, optional
        The minimum longitude of the region within which the estimates
        are considered valid.
    max_lat : scalar, optional
        The maximum latitude of the region within which the estimates
        are considered valid.
    max_lon : scalar, optional
        The maximum longitude of the region within which the estimates
        are considered valid.
    masked : bool, optional
        If True, then invalid data is ignored.
        
    Returns
    -------
    lons : ndarray
        A 1D NumPy array of longitude values.
    lats : ndarray
        A 1D NumPy array of latitude values.
    sm : ndarray
        A 1D NumPy array of surface soil moisture estimates.
    sm_err : ndarray
        A 1D NumPy array of surface soil moisture error estimates.
    times : ndarray
        A 1D NumPy array of datetime objects, representing the sensing
        time for each location specified by `lats` and `lons`.
    angles : ndarray
        A 3D NumPy array of incidence angles for the fore, mid and aft
        ASCAT sensors. The first column is fore and last column is
        aft.
    
    """
    temp_file = False
    
    if eps_fname[-3:] == 'bz2': # compressed file
        fname = eps_fname[:-4]
        
        fp = BZ2File(eps_fname)
        tmp = file(fname, 'wb')
        tmp.write(fp.read())
        fp.close()
        tmp.close()
        
        temp_file = True
        
    else: # assume uncompressed file
        fname = eps_fname
            
    eps_file = eugene.Product(fname)
    if masked:
        eugene.ignore_invalid_values(True)
        
    lons = np.array(eps_file.get("mdr-1b-25km[].LONGITUDE"))
    lats = np.array(eps_file.get("mdr-1b-25km[].LATITUDE"))
    data = np.array(eps_file.get("mdr-1b-25km[].SOIL_MOISTURE"))

    request = "mdr-1b-25km[].RECORD_HEADER.RECORD_START_TIME"
    tm = np.array(eps_file.get(request))
    tm = np.repeat(tm[:, np.newaxis], data.shape[1], axis=1)

    request = "mdr-1b-25km[].INC_ANGLE_TRIP"
    angles = np.array(eps_file.get(request))

    request = "mdr-1b-25km[].SOIL_MOISTURE_ERROR"
    sm_err = np.array(eps_file.get(request))
    
    if (min_lat != None) & (max_lat != None) & \
       (min_lon != None) & (max_lon != None):
        
        condition = (min_lon <= lons) & (lons <= max_lon) \
                    & (min_lat <= lats) & (lats <= max_lat) \
                    & (0 <= data) & (data <= 100)
    else:
        
        condition = (0 <= data) & (data <= 100)
        
    lons = lons[condition].ravel()
    lats = lats[condition].ravel()
    sm = data[condition].ravel()
    sm_err = sm_err[condition].ravel()
    tm = tm[condition].ravel()

    temp = np.empty((lons.size, 3))
    temp[:, 0] = angles[:, :, 0][condition].ravel()
    temp[:, 1] = angles[:, :, 1][condition].ravel()
    temp[:, 2] = angles[:, :, 2][condition].ravel()
    angles = temp
    
    del eps_file # hope to resolve the memory leak
    
    if temp_file:
        os.remove(fname)
    
    return lons, lats, sm, sm_err, tm, angles

def create_soil_moisture_map(fig_fname, lons, lats, 
                             data, boundary_fname=None):
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.basemap import Basemap

    cmin = 0
    cmax = 100
    # create new figure
    fig = Figure()
    ax = fig.add_axes([0.075,0.075,0.75,0.75], axisbg='#D0D0D0')

    # make a plot on a map
    curr_map = Basemap(projection='cyl', llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                        urcrnrlon=ur_lon, urcrnrlat=ur_lat, resolution='l',
                        ax=ax, area_thresh=1000.)

    # transform lons and lats to map coordinates.
    x, y = curr_map(lons, lats)

    im = curr_map.scatter(x, y, s=15, c=data, marker='s',
                          cmap=cm.RdBu, vmin=cmin, vmax=cmax,
                          edgecolors='none')

    # setup colorbar axes and draw colorbar
    bbox = ax.get_position()
    l,b,w,h = bbox.bounds
    cax = fig.add_axes([l+w+0.05, b, 0.05, h],frameon=False)
    fig.colorbar(im, cax=cax)

    # draw country borders
    if boundary_fname is None:
        curr_map.drawcoastlines(linewidth=0.7, color='black')
        curr_map.drawcountries(linewidth=0.7, color='black')
    else:
        curr_map.readshapefile(boundary_fname,
                               'world', drawbounds=True, linewidth=0.7)

    # draw parallels and meridians.
    delat = 5.
    circles = np.arange(0, -45, -delat)
    curr_map.drawparallels(circles, labels=[1,0,0,0])

    delon = 5.
    meridians = np.arange(-10, 60, delon)
    curr_map.drawmeridians(meridians, labels=[0,0,0,1])

#    title = 'ASCAT soil moisture - 2009/02/01'
#    title = 'ASCAT soil moisture - 2008/12/15'
    title = 'ASCAT soil moisture - 2008/08/01'

    fig.text(0.05, 0.9, title, fontweight='bold', fontsize=20)
    fig.text(0.9, 0.015, 'SWI %', fontweight='bold', fontsize=16)

    fig.set_size_inches((9.3, 7))
    canvas = FigureCanvas(fig)
    canvas.print_figure(fig_fname, dpi=100)

def create_error_map(fig_fname, lons, lats, data, boundary_fname=None):
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.basemap import Basemap

    cmin = 0
    cmax = 7.5
    # create new figure
    fig = Figure()
    ax = fig.add_axes([0.075,0.075,0.75,0.75], axisbg='#D0D0D0')

    # make a plot on a map
    curr_map = Basemap(projection='cyl', llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                        urcrnrlon=ur_lon, urcrnrlat=ur_lat, resolution='l',
                        ax=ax, area_thresh=1000.)

    # transform lons and lats to map coordinates.
    x, y = curr_map(lons, lats)

    im = curr_map.scatter(x, y, s=15, c=data, marker='s',
                          cmap=cm.jet, vmin=cmin, vmax=cmax,
                          edgecolors='none')

    # setup colorbar axes and draw colorbar
    bbox = ax.get_position()
    l,b,w,h = bbox.bounds
    cax = fig.add_axes([l+w+0.05, b, 0.05, h],frameon=False)
    fig.colorbar(im, cax=cax)

    # draw country borders
    if boundary_fname is None:
        curr_map.drawcoastlines(linewidth=0.7, color='black')
        curr_map.drawcountries(linewidth=0.7, color='black')
    else:
        curr_map.readshapefile(boundary_fname,
                               'world', drawbounds=True, linewidth=0.7)

    # draw parallels and meridians.
    delat = 5.
    circles = np.arange(0, -45, -delat)
    curr_map.drawparallels(circles, labels=[1,0,0,0])

    delon = 5.
    meridians = np.arange(-10, 60, delon)
    curr_map.drawmeridians(meridians, labels=[0,0,0,1])

#    title = 'ASCAT soil moisture - 2009/02/01'
#    title = 'ASCAT soil moisture error - 2008/12/15'
    title = 'ASCAT soil moisture error - 2008/08/01'

    fig.text(0.05, 0.9, title, fontweight='bold', fontsize=20)
    fig.text(0.9, 0.015, 'Error %', fontweight='bold', fontsize=16)

    fig.set_size_inches((9.3, 7))
    canvas = FigureCanvas(fig)
    canvas.print_figure(fig_fname, dpi=100)
