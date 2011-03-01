"""
A collection of par-cooked plots. Just add data and textual seasoning
to your taste.

"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from mpl_toolkits.basemap import Basemap

def rsa_lat_lon_scatter(fig_fname, title,
                        lons, lats, data, cmap, norm,
                        boundary_fname=None, grid_color='#BDBDBD'):
    """
    Plot a colour-mapped scatter plot over RSA.

    This function returns a Matplotlib ListedColormap using the color
    specifications from the ColorBrewer (http://colorbrewer.org)
    palettes.

    Parameters
    ----------
    fig_fname : string
        The name of the file to save the resulting figure. The file
        extension determines the format of the saved file, just like
        Matplotlib.
    title : string
        The title to add to the figure.
    lons : array_like
        A list of the longitudes of the data point positions.
    lats : array_like
        A list of the latitudes of the data point positions.
    data : array_like
        A list of the data values at the points located at the
        positions specified by `lons` and `lats`.
    cmap : matplotlib.colors.Colormap
        A Matplotlib Colormap instance to be used as the figure
        colormap.
    norm : matplotlib.colors.Normalize
        A Matplotlib Normalize instance to distribute the data over
        the given color range.
    boundary_fname : string
        The name of a shapefile containing country borders.
    grid_color : Matplotlib color spec
        A valid color specification for Matplotlib. The data grid and
        labels are plotted in this color. Default is a light gray.

    Returns
    -------
    Nothing

    """
    # define domain
    ll_lon = 15
    ll_lat = -35
    ur_lon = 35
    ur_lat = -20

    # create new figure
    fig = plt.figure()
    ax = fig.add_axes([0.075, 0.1, 0.75, 0.75])

    # make a plot on a map
    curr_map = Basemap(projection='cyl', llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                        urcrnrlon=ur_lon, urcrnrlat=ur_lat, resolution='l',
                        ax=ax, area_thresh=1000.)

    # transform lons and lats to map coordinates.
    x, y = curr_map(lons, lats)

    im = curr_map.scatter(x, y, s=7, c=data, marker='o',
                          cmap=cmap, norm=norm, edgecolors='none', zorder=100)

    # setup colorbar axes and draw colorbar
    bbox = ax.get_position()
    l,b,w,h = bbox.bounds
    cax = fig.add_axes([l+w+0.05, b, 0.05, h],frameon=False)
    fig.colorbar(im, cax=cax)

    # draw country borders
    if boundary_fname is None:
        curr_map.drawcoastlines(linewidth=1.0)
        curr_map.drawcountries(linewidth=1.0)
    else:
        curr_map.readshapefile(boundary_fname, 'world',
                               drawbounds=True,
                               linewidth=0.5, color=grid_color)

    # draw parallels and meridians.
    delat = 5.
    circles = np.arange(0, -45, -delat)
    p = curr_map.drawparallels(circles, labels=[1,0,0,0],
                               linewidth=0.4, color=grid_color)

    for key in p:
        text = p[key][1][0] # The Text object for each parallel
        text.set_color(grid_color)

    delon = 5.
    meridians = np.arange(-10, 60, delon)
    yoffset = (curr_map.urcrnry - curr_map.llcrnry)/50.0
    if curr_map.aspect > 1:
        yoffset = curr_map.aspect*yoffset
    else:
        yoffset = yoffset/curr_map.aspect

    m = curr_map.drawmeridians(meridians,
                               labels=[0,0,0,1],
                               linewidth=0.4, color=grid_color, yoffset=yoffset)

    for key in m:
        text = m[key][1][0] # The Text object for each meridian
        text.set_color(grid_color)

    ax.set_title(title, y=1.05, fontweight='bold', fontsize=20)

    curr_map.drawmapboundary(linewidth=0.5, color=grid_color)

    fig.set_size_inches((8, 6))
    plt.savefig(fig_fname, dpi=100)

def regression_plot(x, y, fig_name,
                    xlabel='x', ylabel='y', title='scatter plot'):
    """Fit and plot a linear regression model through the data."""
    import scikits.statsmodels as sm

    x = np.asanyarray(x)
    X = sm.add_constant(x)
    y = np.asanyarray(y)
    Y = np.array(y)
    
    # fit a linear regression model
    model = sm.OLS(Y, X)
    results = model.fit()
    a, b = results.params

    x = np.unique(x) # avoid MPL path simplification bug
    y_hat = a*x + b

    if b < 0:
        info = u'Fitted line: %2.3fx - %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), results.rsquared)
    elif b == 0:
        info = u'Fitted line: %2.3fx \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, results.rsquared)
    else:
        info = u'Fitted line: %2.3fx + %2.3f \nR\N{SUPERSCRIPT TWO} = %2.3f' % (a, abs(b), results.rsquared)


    # plot the results
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    maxm = max(x.max(), y.max())
    minm = min(x.min(), y.min())

    maxm += 0.1*maxm
    minm -= 0.1*maxm

    # 1:1 line
    ax.plot([minm, maxm], [minm, maxm], '--', color='lightgrey')

    ax.plot(x , y_hat, '-', c='gray', linewidth=2)
    ax.scatter(X[:, 0], y, s=15, c='k')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.yaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)
    ax.xaxis.grid(True, linestyle='-',
                  which='major', color='lightgrey', alpha=0.4)

    # Hide grid behind plot objects
    ax.set_axisbelow(True)

    ax.set_xlim(minm, maxm)
    ax.set_ylim(minm, maxm)

    ax.text((0.05*maxm) + minm, 0.875*maxm,
            info, fontweight='bold', fontsize=12)

    # save figure
    base, name = os.path.split(fig_name)
    if not os.path.isdir(base) and base != '':
        os.makedirs(base)

    fig.savefig(fig_name)
