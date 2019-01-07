from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

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
from compas.geometry import weighted_centroid_points

from compas.geometry import centroid_points

from compas.geometry import bestfit_plane
from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import intersection_line_line
from compas.geometry import is_point_on_segment
from compas.geometry.intersections import intersection_segment_segment
from compas.geometry.transformations.transformations import project_point_plane

from compas.datastructures.network import Network

from compas.utilities import geometric_key

from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_faces


__all__  = ['resultant_vector',
            'datastructure_centroid',

            'normal_polygon_general',
            'area_polygon_general',

            'volmesh_face_flatness',
            'volmesh_face_areaness']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   vectors
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def resultant_vector(vectors, locations):

    points  = []
    weights = []

    for vkey in vectors:
        points.append(vectors[vkey])
        weights.append(length_vector(vectors[vkey]))

    resultant_xyz = weighted_centroid_points(points, weights)
    x, y, z = zip(*vectors.values())
    resultant_vector = [sum(x), sum(y), sum(z)]

    return resultant_xyz, resultant_vector


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   polygons
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
    points : sequence
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
#   volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_face_flatness(volmesh):
    """Compute volmesh flatness per face.

    Parameters
    ----------
    volmesh : volmesh object

    Returns
    -------
    dict
        A dictionary of flatness deviation for each face.

    Noes
    ----
    compas.geometry.mesh_flatness function currently only works for quadrilateral faces.
    This function uses the distance between each face vertex and its projected point on the best-fit plane of the face as the flatness metric.

    See Also
    --------
    * :func: `compas.geometry.mesh_flatness`

    """
    flatness_dict = {fkey : 0 for fkey in volmesh.faces()}
    for fkey in volmesh.faces():
        deviation = 0
        f_vkeys   = volmesh.halfface_vertices(fkey)
        f_points  = [volmesh.vertex_coordinates(vkey) for vkey in f_vkeys]
        plane     = bestfit_plane(f_points)
        for vkey in f_vkeys:
            xyz   = volmesh.vertex_coordinates(vkey)
            p_xyz = project_point_plane(xyz, plane)
            dev   = distance_point_point(xyz, p_xyz)
            if dev > deviation:
                deviation = dev
        flatness_dict[fkey] = deviation
    return flatness_dict


def volmesh_face_areaness(volmesh, target_areas):
    """Compute volmesh areaness of faces with given target areas.
    """
    areaness_dict = {}
    for hfkey in target_areas:
        area = volmesh.halfface_area(hfkey)
        areaness_dict[hfkey] = abs(target_areas[hfkey] - area)
    return areaness_dict


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   datastructures
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def datastructure_centroid(datastructure):
    points = [datastructure.vertex_coordinates(vkey) for vkey in datastructure.vertex]
    return centroid_points(points)



# def is_polygon_self_intersecting(points):
#     """Computes if as polygon is self intersecting in plane, or self overlapping in space.

#     Parameters
#     ----------
#     polygon : sequence
#         The XYZ coordinates of the vertices/corners of the polygon.
#         The vertices are assumed to be in order.
#         The polygon is assumed to be closed:
#         the first and last vertex in the sequence should not be the same.

#     Returns
#     -------
#     bool_1
#         ``True`` if self overlapping.
#         ``False`` otherwise.
#     bool_2
#         ``True`` if self intersecting.
#         ``False`` otherwise.

#     """
#     edges = []
#     for i in range(-1, len(points) - 1):
#         edges.append((i, i + 1))

#     for u1, v1 in edges:
#         for u2, v2 in edges:
#             if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
#                 continue
#             else:
#                 a = points[u1]
#                 b = points[v1]
#                 c = points[u2]
#                 d = points[v2]

#                 int_1, int_2 = intersection_line_line((a, b), (c, d))

#                 if int_1 or int_2:
#                     if distance_point_point(int_1, int_2) > 0:
#                         overlapping = True
#                     if is_point_on_segment(int_1, (a, b)) or is_point_on_segment(int_2, (c, d)):
#                             intersecting = True

#     return overlapping, intersecting