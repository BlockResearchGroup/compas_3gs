from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import Rhino
import rhinoscriptsyntax as rs

from math import pi

from compas.geometry import orient_points

from compas.geometry import angle_vectors
from compas.geometry import is_ccw_xy
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import angle_vectors
from compas.geometry import translate_points
from compas.geometry import rotate_points
from compas.geometry import area_polygon
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import normal_polygon
from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.geometry import centroid_points

from compas.geometry import distance_point_point as distance
from compas.geometry import is_point_on_segment
from compas.geometry import intersection_line_line
from compas.geometry.intersections import intersection_segment_segment


from compas.datastructures.network import Network

from compas.utilities import geometric_key

from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_faces


__all__ = [
    'normal_polygon_general',
    'area_polygon_general',
]


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   self-intersecting polygons
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def normal_polygon_general(points, unitized=True):
    """Compute the oriented normal of any closed polygon (can be convex, concave or complex).

    Parameters
    ----------
    points : sequence
        The XYZ coordinates of the vertices/corners of the polygon.
        The vertices are assumed to be in order.
        The polygon is assumed to be closed:
        the first and last vertex in the sequence should not be the same.

    Returns
    -------
    list
        The weighted or unitized normal vector of the polygon.

    """
    p = len(points)
    assert p > 2, "At least three points required"
    w          = centroid_points(points)
    normal_sum = (0, 0, 0)
    for i in range(-1, len(points) - 1):
        u          = points[i]
        v          = points[i + 1]
        uv         = subtract_vectors(v, u)
        vw         = subtract_vectors(w, v)
        normal     = scale_vector(cross_vectors(uv, vw), 0.5)
        normal_sum = add_vectors(normal_sum, normal)
    if not unitized:
        return normal_sum
    return normalize_vector(normal_sum)


def area_polygon_general(points):
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
    return length_vector(normal_polygon_general(points, unitized=False))










# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   self-intersecting polygons
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def is_polygon_self_intersecting(points):
    """Computes if as polygon is self intersecting in plane, or self overlapping in space.

    Parameters
    ----------
    polygon : sequence
        The XYZ coordinates of the vertices/corners of the polygon.
        The vertices are assumed to be in order.
        The polygon is assumed to be closed:
        the first and last vertex in the sequence should not be the same.

    Returns
    -------
    bool_1
        ``True`` if self overlapping.
        ``False`` otherwise.
    bool_2
        ``True`` if self intersecting.
        ``False`` otherwise.

    """
    edges = []
    for i in range(-1, len(points) - 1):
        edges.append((i, i + 1))

    for u1, v1 in edges:
        for u2, v2 in edges:
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = points[u1]
                b = points[v1]
                c = points[u2]
                d = points[v2]

                int_1, int_2 = intersection_line_line((a, b), (c, d))

                if int_1 or int_2:
                    if distance_point_point(int_1, int_2) > 0:
                        overlapping = True
                    if is_point_on_segment(int_1, (a, b)) or is_point_on_segment(int_2, (c, d)):
                            intersecting = True

    return overlapping, intersecting


