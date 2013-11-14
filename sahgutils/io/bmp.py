import struct

import numpy as np

class BMPFile:
    """Class for read operations on 8-bit BMP files.

    This class handles a very specific subset of valid bitmap
    files. Namely 256 colour (8-bit) colour paletted bitmap files.

    """
    def __init__(self, filename):
        self.filename = filename

        self._header_fmt = '=2sihhiiiihhiiiiii'
        self._palette_fmt = 'BBBB'*256

        self._header_length = 54
        self._palette_length = 1024

        with open(filename, 'rb') as self._fp:
            self._read_header()
            self._read_palette()
            self._read_data()

    # Internal methods

    # Adapted from http://blog.cykerway.com/post/65 accessed
    # 2013-11-13
    def _read_header(self):
        #read header
        header_fmt = '=2sihhiiiihhiiiiii'
        header_length = 54

        s_header = self._fp.read(header_length)

        print '----Header----'
        for it in struct.unpack(header_fmt, s_header):
          print it

    def _read_palette(self):
        #read palette
        palette_fmt = 'BBBB'*256
        palette_length = 1024

        s_palette = self._fp.read(palette_length)
        palette = struct.unpack(palette_fmt, s_palette)

        print '----palette----'
        i = 0
        while i < len(palette):
          print palette[i:i+4]
          i += 4

    def _read_data(self):
        #read data
        print '----Data----'
        data_string = self._fp.read()

        data = np.fromstring(data_string, np.int8)

        data = data.reshape(128, 128)
        data = np.flipud(data)

        print(data)
