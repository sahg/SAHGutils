import struct

import numpy as np

class BMPFile:
    """Class for read operations on 8-bit BMP files.

    This class handles a very specific subset of valid bitmap
    files. Namely 256 colour (8-bit) colour paletted bitmap files.

    Example usage:

    >>> bmp_file = BMPFile(filename)

    >>> print('---HEADER---')
    >>> bmp_header = bmp_file.header()
    >>> print(bmp_header)

    >>> print('---PALETTE---')
    >>> bmp_palette = bmp_file.palette()
    >>> print(bmp_palette)

    >>> print('---DATA---')
    >>> bmp_data = bmp_file.data()
    >>> print(bmp_data)

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

    # Header and palette reading code adapted from
    # http://blog.cykerway.com/post/65 accessed 2013-11-13
    def _read_header(self):
        #read header
        header_fmt = '=2sihhiiiihhiiiiii'
        header_length = 54

        s_header = self._fp.read(header_length)
        self._header = struct.unpack(header_fmt, s_header)

    def _read_palette(self):
        #read palette
        palette_fmt = 'BBBB'*256
        palette_length = 1024

        s_palette = self._fp.read(palette_length)
        self._palette = struct.unpack(palette_fmt, s_palette)

    def _read_data(self):
        #read data
        data_string = self._fp.read()

        self._data = np.fromstring(data_string, np.int8)

        self._data = self._data.reshape(self._header[7], self._header[6])

        # Bitmap data origin is stored at bottom left
        self._data = np.flipud(self._data)

    # API methods
    def header(self):
        """Return the file header.

        Returns the file header as a dictionary.

        """
        header = {
                  'signature' : self._header[0],
                  'filesize' : self._header[1],# header + palette + data
                  'reserved1' : self._header[2],
                  'reserved2' : self._header[3],
                  'dataoffset' : self._header[4],# header + palette
                  'headersize' : self._header[5],
                  'datawidth' : self._header[6],
                  'dataheight' : self._header[7],
                  'colourplanes' : self._header[8],
                  'colourdepth' : self._header[9],
                  'compression' : self._header[10],# 0 = no compression
                  'imagesize' : self._header[11],# width * height
                  'horizres' : self._header[12],# pixels per metre
                  'vertres' : self._header[13],# pixels per metre
                  'colours' : self._header[14],# 2^colourdepth
                  'coloursused' : self._header[15],# num of colours in image
                  }

        return header

    def palette(self):
        """Return the palette as RGBA tuples.

        Returns the colour palette entries in a list of RGBA tuples.

        """
        colour_palette = []
        i = 0
        while i < len(self._palette):
            # Palette stored in BGRA order in BMP
            blue = self._palette[i]
            green = self._palette[i+1]
            red = self._palette[i+2]
            alpha = self._palette[i+3]

            colour_palette.append((red, green, blue, alpha))

            i += 4

        return colour_palette

    def data(self):
        """Return the data portion of the image.

        Returns the image data as an 8-bit integer 2D numpy array.

        """
        return self._data
