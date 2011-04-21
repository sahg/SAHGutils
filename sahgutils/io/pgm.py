"""Utilities for reading and plotting EUMETSAT Cloud Mask data.

This module contains some simple functions to make it easier
to read and plot the Multisensor Precipitation Estimate (MPE)
data produced by EUMETSAT. The data are provied in GRIB2 files
and the module currently relies on Wesley Ebisuzaki's
wgrib2 programme being somewhere on your systems path. If you
don't have wgrib2 it can be obtained from:

http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/

"""

import os
import sys

import numpy as np
from numpy import ma

import pylab as pl

def execute(command):
    """Execute a system command passed as a string."""
    
    print 'Running:', command
    os.system(command)
    print '--------------------\n'
    
def read_sensor_count(pgm_name):
    """Read the MPE data from a grib file into an array.

    This function uses wgrib2 to write and then read the MPE
    data via an intermediate binary file, which is later
    deleted. The non-raining regions are masked and the data
    converted into mm/hr.

    """

    bin_name = pgm_name[0:-4] + '.bin'
    hdr_name = pgm_name[0:-4] + '.hdr'

    exec_str = 'gdal_translate -ot UInt16 -of EHdr ' + pgm_name + ' ' + bin_name # spaces are N.B.

    execute(exec_str)
    data = np.fromfile(bin_name, dtype=np.uint16)
    os.remove(bin_name)
    os.remove(hdr_name)

    # read the pgm header and parse for relevant parameters
    f = open(pgm_name)
    pgm_hdr = f.read(120)
    f.close()

    hdr_elems = pgm_hdr.split()    
    
    cols = int(hdr_elems[1]) # fixed if the pgm format spec is followed
    rows = int(hdr_elems[2]) # fixed if the pgm format spec is followed

    data = np.reshape(data, (rows, cols))
    data = ma.masked_values(data, 0)

    return data    

def read_radiance(pgm_name):
    """Read the MPE data from a grib file into an array.

    This function uses wgrib2 to write and then read the MPE
    data via an intermediate binary file, which is later
    deleted. The non-raining regions are masked and the data
    converted into mm/hr.

    """

    bin_name = pgm_name[0:-4] + '.bin'
    hdr_name = pgm_name[0:-4] + '.hdr'

    exec_str = 'gdal_translate -ot UInt16 -of EHdr ' + pgm_name + ' ' + bin_name # spaces are N.B.

    execute(exec_str)
    data = np.fromfile(bin_name, dtype=np.uint16)
    os.remove(bin_name)
    os.remove(hdr_name)

    # read the pgm header and parse for relevant parameters
    f = open(pgm_name)
    pgm_hdr = f.read(120)
    f.close()

    hdr_elems = pgm_hdr.split()    
    
    cols = int(hdr_elems[1]) # fixed if the pgm format spec is followed
    rows = int(hdr_elems[2]) # fixed if the pgm format spec is followed

    ind = pgm_hdr.find('offset=')
    offset_str = pgm_hdr[ind:].split('\n')[0]
    offset_str = offset_str.split()[0]
    offset = float(offset_str.split('=')[1])

    ind = pgm_hdr.find('slope=')
    slope_str = pgm_hdr[ind:].split('\n')[0]
    slope = float(slope_str.split('=')[1])

    data = np.reshape(data, (rows, cols))
    data = ma.masked_values(data, 0)

    # compute the radiance from the raw sensor counts
    data = offset + slope*data
    
    return data    

def read_btemp(pgm_name):
    """Read the MPE data from a grib file into an array.

    This function uses wgrib2 to write and then read the MPE
    data via an intermediate binary file, which is later
    deleted. The non-raining regions are masked and the data
    converted into mm/hr.

    """

    data = read_radiance(pgm_name)

    # compute brightness temp from radiance
    C1 = 1.19104E-5
    C2 = 1.43877

    if (pgm_name.find('ch09')):
##    if (pgm_name[17:21] == 'ch09'):
##        print '%s is channel 09 data' % pgm_name
        A = 0.9983
        B = 0.627
        nu = 930.659
    elif (pgm_name.find('ch10')):
##        print '%s is channel 10 data' % pgm_name
        A = 0.9988
        B = 0.397
        nu = 839.661
    else:
        print 'Unknown file naming convention'

    data = np.log(((C1*nu**3)/data) + 1) - B        
    data = ((C2*nu)/data)/A        
    
    return data    

def plot(pgm_name, fig_name, title='PGM Plot'):
    """Create a plot of the data in a GRIB2 file."""
    
    a = read_sensor_count(pgm_name)

    pl.clf()
    pl.axes(axisbg='black')
    pl.imshow(a, interpolation='nearest', origin='upper')
    pl.colorbar()
    pl.title(title)
    pl.clim(0, 1023)
    pl.savefig(fig_name)
    pl.close()

