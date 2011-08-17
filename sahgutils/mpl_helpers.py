"""
A collection of helper functions to aid the construction of custom
figures using Matplotlib and Basemap.

"""
from matplotlib.colors import ListedColormap

from _color_brewer import cdict

def _search_key(cmap_name):
    cat_range = range(3, 13)
    cat_range.reverse()

    for cat in cat_range:
        pal_name = '_%s_cat%s_data' % (cmap_name, cat)

        if pal_name in cdict:
            break

    return pal_name
    
def categorical_cmap(cmap_name, num_cat=None, reverse=False):
    """
    Construct a Matplotlib ListedColormap using ColorBrewer palettes.

    This function returns a Matplotlib ListedColormap using the color
    specifications from the ColorBrewer (http://colorbrewer.org)
    palettes.

    Parameters
    ----------
    cmap_name : string
        The name of the ColorBrewer palette to use for constructing
        the ListedColormap e.g. 'Purples', 'RdBu' etc.
    num_cat : int, optional
        The number of distinct colors (categories) to use in creating
        the colourmap. If `num_cat` is unspecified or larger than the
        maximum size of the colourmap, then a colormap with the
        maximum number of categories is returned. The number of
        catergories in the returned `cmap` can be determined using
        `cmap.N`.
    reverse : bool, optional
        Whether to reverse the entries in the colormap. Default is
        False.

    Returns
    -------
    cmap : matplotlib.colors.ListedColormap
        A ListedColormap constructed using the given parameters is
        returned.

    """
    if num_cat is not None:
        pal_name = '_%s_cat%s_data' % (cmap_name, int(num_cat))

        if pal_name not in cdict:
            pal_name = _search_key(cmap_name)

    else:
        pal_name = _search_key(cmap_name)

    clist = cdict[pal_name]
    if reverse is True:
        clist.reverse()

    cmap = ListedColormap(clist)

    return cmap
