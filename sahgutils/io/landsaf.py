"""Utilities for reading LSA-SAF product files.

This module contains some functions for reading the data products produced by
the Land Surface Analysis Satellite Applications Facility (http://landsaf.meteo.pt).
The data products are distributed in HDF5 format and therefore the module requires
the PyTables package. Numpy is also used.

"""
import os
from bz2 import BZ2File
from datetime import datetime

import numpy as np
import tables as h5

from numpy import ma

def parse_file_name(file_name):
    """Parse an LSA-SAF file name to get the slot time.
    
    A datetime object containg the slot time (in UTC) is returned.
    
    """
    # HDF5_LSASAF_MSG_DSLF_SAfr_200702211000.h5 or S-LSA_-HDF5_LSASAF_MSG_DSLF_SAfr_200707260830 etc.
    indx = file_name.rfind('_') + 1
    year = int(file_name[indx:indx+4])
    month = int(file_name[indx+4:indx+6])
    day = int(file_name[indx+6:indx+8])
    hour = int(file_name[indx+8:indx+10])
    min = int(file_name[indx+10:indx+12])

    return datetime(year, month, day, hour, min)

def _read_raw(file_name, data_node_name, quality_node_name):
    """Return the raw data and quality control flags.

    This function returns the data as stored in the HDF5 data and q_flag arrays.
    The scaling factors are applied. Use this function if you need to do your own
    (non-standard) masking of the LSA-SAF data. Numpy arrays are returned with
    the same shape as the HDF5 data arrays. The returned data array has type float32
    and the flags aray has the same type as the data in the HDF5 file.

    """
    h5file = h5.openFile(file_name)
    
    node = h5file.getNode(data_node_name)
    data = node.read()
    data = np.asarray(data, np.float32)
    if (node._v_attrs.SCALING_FACTOR != 1):
        data /= node._v_attrs.SCALING_FACTOR

    node = h5file.getNode(quality_node_name)
    flags = node.read()
        
    h5file.close()

    return data, flags

def read_lst(file_name):
    """Get a masked array containing the LST values.

    Sea, space and severly contaminated pixels are masked out. The masked array
    returned by this function contains the LST in degrees Centigrade.

    """
    # _read_raw() requires an uncompressed HDF5 file
    if file_name[-3:] == 'bz2':
        # create a temp file
        temp_fname = 'temp.h5'
        
        bz2_file = BZ2File(file_name)
        fp = open(temp_fname, 'wb')
        fp.write(bz2_file.read())
        fp.close()
        bz2_file.close()

        data, flags = _read_raw(temp_fname, '/LST', '/Q_FLAGS')
        
        os.remove(temp_fname)
    else:
        data, flags = _read_raw(file_name, '/LST', '/Q_FLAGS')

    # mask based on the quality flags
    data = ma.masked_where(flags == 0, data)# sea pixel
    data = ma.masked_where(flags == 4, data)# corrupted pixel
    data = ma.masked_where(flags == 12, data)# CMa - pixel non processed
    data = ma.masked_where(flags == 44, data)# CMa - pixel contaminated by clouds
    data = ma.masked_where(flags == 60, data)# CMa - Cloud filled
    data = ma.masked_where(flags == 76, data)# CMa - contaminated by snow/ice
    data = ma.masked_where(flags == 92, data)# CMa - Undefined
    data = ma.masked_where(flags == 28, data)# Emissivity Information Missing
    data = ma.masked_where(flags == 156, data)# Viewing Angle Out of Range (EM Poor)
    data = ma.masked_where(flags == 284, data)# Viewing Angle Out of Range (EM Nominal)
    data = ma.masked_where(flags == 412, data)# Viewing Angle Out of Range (EM Excellent)
    data = ma.masked_where(flags == 668, data)# cwv information missing
    data = ma.masked_where(flags == 796, data)# cwv information missing
    data = ma.masked_where(flags == 924, data)# cwv information missing
##    data = ma.masked_where(flags == 5790, data)# Below Nominal (+ EM below nominal)
##    data = ma.masked_where(flags == 5918, data)# Below Nominal (+ EM nominal)
##    data = ma.masked_where(flags == 6046, data)# Below Nominal (+ EM above nominal)
##    data = ma.masked_where(flags == 10014, data)# Nominal (EM nominal)
##    data = ma.masked_where(flags == 10142, data)# Nominal (EM above nominal)
##    data = ma.masked_where(flags == 14238, data)# Above Nominal (EM above nominal)

    return data

def read_dslf(file_name):
    """Get a masked array containing the DSLF values.

    Sea, space and severly contaminated pixels are masked out. The masked array
    returned by this function contains the DSLF in W/m^2.

    """

    data, flags = _read_raw(file_name, '/DSLF', '/Q_FLAGS')

    # mask based on the quality flags
    data = ma.masked_where(flags == 0, data)# sea or space pixel
    data = ma.masked_where(flags == 4, data)# T2m missing
    data = ma.masked_where(flags == 12, data)# CMa - pixel non processed
    data = ma.masked_where(flags == 92, data)# CMa - Undefined
    data = ma.masked_where(flags == 156, data)# TPW information missing
    data = ma.masked_where(flags == 44, data)# CTTH_EFFECTIVE missing (CMa - pixel contaminated by clouds)
    data = ma.masked_where(flags == 60, data)# CTTH_EFFECTIVE missing (CMa - Cloud filled)
    data = ma.masked_where(flags == 76, data)# CTTH_EFFECTIVE missing (CMa - contaminated by snow/ice)
    data = ma.masked_where(flags == 812, data)# Td2m missing (CMa - pixel contaminated by clouds)
    data = ma.masked_where(flags == 828, data)# Td2m missing (CMa - Cloud filled)
    data = ma.masked_where(flags == 844, data)# Td2m missing (CMa - contaminated by snow/ice)
##    data = ma.masked_where(flags == 11422, data)# Below Nominal (CMa - Cloud-free)
##    data = ma.masked_where(flags == 19614, data)# Nominal (CMa - Cloud-free)
##    data = ma.masked_where(flags == 27806, data)# Above Nominal (CMa - Cloud-free)
##    data = ma.masked_where(flags == 13102, data)# Below Nominal (CMa - pixel contaminated by clouds)
##    data = ma.masked_where(flags == 21294, data)# Nominal (CMa - pixel contaminated by clouds)
##    data = ma.masked_where(flags == 29486, data)# Above Nominal (CMa - pixel contaminated by clouds)
##    data = ma.masked_where(flags == 13118, data)# Below Nominal (CMa - Cloud filled)
##    data = ma.masked_where(flags == 21310, data)# Nominal (CMa - Cloud filled)
##    data = ma.masked_where(flags == 29502, data)# Above Nominal (CMa - Cloud filled)
##    data = ma.masked_where(flags == 13134, data)# Below Nominal (CMa - contaminated by snow/ice)
##    data = ma.masked_where(flags == 21326, data)# Nominal(CMa - contaminated by snow/ice)
##    data = ma.masked_where(flags == 29518, data)# Above Nominal (CMa - contaminated by snow/ice)

    return data

def _get_bit_value(n, p):
    """
    get the bitvalue of denary (base 10) number n at the equivalent binary
    position p (binary count starts at position 0 from the right)
    """
    return (n >> p) & 1

def _test_bit_values(n, p):
    """
    Test the bitvalue of denary (base 10) number n at the equivalent binary
    position p (binary count starts at position 0 from the right)
    """
    _get_bit_value(n, p)
    
    return (n >> p) & 1

def read_dssf(file_name):
    """Get a masked array containing the DSSF values.

    Sea, space and severly contaminated pixels are masked out. The mask is defined
    according to the bitfield specified in SAF_LAND_MF_PUM_DSSF_1.4.pdf. The
    masked array returned by this function contains the DSSF in W/m^2.

    """
    data, flags = _read_raw(file_name, '/DSSF', '/DSSF_Q_Flag')

    # mask based on the quality flags [THIS IS STILL INCOMPLETE!!!]
    data = ma.masked_where(flags == 0, data)# ocean pixel [Always masked]
    data = ma.masked_where(flags == 2, data)# space pixel [Always masked]

    return data
