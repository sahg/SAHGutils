"""Utilities for reading and plotting MDV files.

This module contains some simple functions to make it easier
to read and plot the data from MDV files produced
by SAWS. The module relies on Scott Sinclair's
mdv2ASCII programme being somewhere on your systems path.

If you don't have mdv2ASCII it can be obtained from:

http://www.??????

"""

import os
import sys

import numpy as np
import pylab as pl
import matplotlib as mpl

my_dict = {'red':   ((0    , 1 , 1  ),
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

def execute(command):
    """Execute a command passed as a string."""
    
    print '\nRunning:', command
    os.system(command)
    print 'Done----------------\n'
    
def read_mdv(mdv_name, field=0, level=0):
    """Read the data field from an MDV file into an array.

    This function uses mdv2ASCII to write and then read the MDV
    data to an intermediate ascii format, which is later
    deleted.

    """
    
    txt_name = mdv_name[0:-4] + '.txt'

    exec_str = 'mdv2ASCII %s %d %d %s' % (mdv_name, field, level, txt_name)

    execute(exec_str)
    a = pl.load(txt_name)
    os.remove(txt_name)

    return a

def mdv_plot(mdv_name, fig_name, title=None, field=0, level=0):
    """Create a plot of the data in an MDV file."""

    if title == None:
        title = '%s:%s:%s' % (mdv_name[-10:-8], mdv_name[-8:-6], mdv_name[-6:-4])
        
    a = read_mdv(mdv_name, field, level)

    my_cmap = mpl.colors.LinearSegmentedColormap('my_colormap', my_dict, 256)
     
##    pl.imshow(np.flipud(a), interpolation='nearest')
    pl.imshow(a, cmap=my_cmap, interpolation='nearest')
    pl.clim(0, 60)
##    pl.clim(-30, 55)
    pl.grid()
    pl.colorbar()
    pl.title(title)
    pl.savefig(fig_name)
    pl.close()

