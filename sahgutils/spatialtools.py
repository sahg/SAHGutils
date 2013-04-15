"""A collection of tools for spatial data and GIS tasks.

"""

def point_in_poly(pnt, poly):
    """Calculate whether a point lies inside a polygon

    Algorithm is based on the ray-tracing procedure described at
    http://geospatialpython.com/2011/01/point-in-polygon.html

    Parameters
    ----------
    pnt : seq
        A point (x, y), which should be a two-element sequence object.
    poly : seq
        A sequence of points describing the polygon.

    Returns
    -------
    True if `pnt` is inside `poly`, False otherwise.

    """
    x, y = pnt
    
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

