"""
This module contains a class for reading the daily rainfall station
files provided by the University of Cape Town's Climate Systems
Analysis Group.

"""
__all__ = ['CSAGStationReader']

from datetime import datetime

import numpy as np

class CSAGStationReader():
    """Class for read operations on CSAG rainfall station files.

    Example Usage:

    >>> from sahgutils.io import CSAGStationReader
    >>> csag_reader = CSAGStationReader('data/CSAG/0001517_.txt')
    >>> header = csag_reader.header()
    >>> dates = csag_reader.dates()
    >>> precip = csag_reader.data()

    """
    def __init__(self, filename, header_rows=65):
        self.filename = filename
        self._header_rows = header_rows
        self._read_header()

        self._data_read = False

    def _read_header(self):
        fp = open(self.filename)

        self._header = {}

        line_indx = 0
        while line_indx  < self._header_rows:
            line = fp.readline()
            if line[0] != '#':
                items = line.split()

                if len(items) >= 1:
                    self._header[items[0]] = items[-1]

            line_indx += 1

        fp.close()

        # convert floats
        keys = ['ALTITUDE', 'LATITUDE', 'LONGITUDE']

        for key in keys:
            if key in self._header.keys():
                val = float(self._header[key])
                self._header[key] = val

        # convert ints
        keys = ['CLEANING']

        for key in keys:
            if key in self._header.keys():
                val = int(self._header[key])
                self._header[key] = val

        # convert dates
        keys = ['CREATED', 'START_DATE', 'END_DATE']

        for key in keys:
            if key in self._header.keys():
                val = datetime.strptime(self._header[key], '%Y%m%d')
                self._header[key] = val

    def _read_data(self):
        self._data = np.genfromtxt(self.filename, delimiter=',',skip_header=66,
                                   dtype=['S9', 'S8', 'S8',
                                          'f8', 'S4', 'S4'],
                                   autostrip=True, names=True)
        # Mask no-data values (defined as -999.0)
        self._data['VAR'][self._data['VAR'] < 0] = np.nan
        self._data_read = True

    def header(self):
        """Return the file header in a dictionary"""
        return self._header

    def data(self):
        """Return the station data as an array"""
        if not self._data_read:
            self._read_data()

        return self._data['VAR']

    def dates(self):
        """Return a list of observation dates"""
        if not self._data_read:
            self._read_data()

        _dates = []
        for ds in self._data['DATE']:
            _dates.append(datetime.strptime(ds, '%Y%m%d'))

        return _dates
