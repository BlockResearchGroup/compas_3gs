from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs

from compas.geometry.basic import subtract_vectors
from compas.geometry.basic import length_vector
from compas.geometry.basic import cross_vectors
from compas.geometry.basic import add_vectors

from compas.geometry.average import centroid_points


def polygon_area_oriented(polygon):
    """Compute the area of a polygon (can be convex or concave).

    Parameters
    ----------
    polygon : sequence
        The XYZ coordinates of the vertices/corners of the polygon.
        The vertices are assumed to be in order.
        The polygon is assumed to be closed:
        the first and last vertex in the sequence should not be the same.

    Returns
    -------
    float
        The area of the polygon.

    """
    w = centroid_points(polygon)

    normal_sum = (0, 0, 0)

    for i in range(-1, len(polygon) - 1):
        u          = polygon[i]
        v          = polygon[i + 1]
        uv         = subtract_vectors(v, u)
        vw         = subtract_vectors(w, v)
        normal     = cross_vectors(uv, vw)
        normal_sum = add_vectors(normal_sum, normal)

    a = 0.5 * length_vector(normal_sum)

    return a


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    guid = rs.GetObject("select polysurfaces", filter=4)
    rs.HideObjects(guid)
    if not rs.IsCurveClosed(guid):
        print('not a closed polyline')

    points        = [[pt.X, pt.Y, pt.Z] for pt in rs.PolylineVertices(guid)]
    points        = points[:-1]

    print(polygon_area_oriented(points))
