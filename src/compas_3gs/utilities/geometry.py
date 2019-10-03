from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import weighted_centroid_points
from compas.geometry import centroid_points
from compas.geometry import midpoint_point_point
from compas.geometry import bestfit_plane
from compas.geometry import distance_point_point
from compas.geometry import intersection_line_line
from compas.geometry import is_point_on_segment
from compas.geometry import project_point_plane


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__  = ['resultant_vector',

            'polygon_normal_oriented',
            'polygon_area_oriented',
            'polygon_area_footprint',
            'scale_polygon',

            'cell_face_flatness',
            'cell_face_areaness',

            'volmesh_face_flatness',
            'volmesh_face_areaness',

            'datastructure_centroid']


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
    """Computes the resultant vector of a group of vectors.

    Parameters
    ----------
    vectors: dictionary
        vector_key-XYZ (vector components) pairs

    locations: dictionary
        vector_key-XYZ (vector locations) pairs

    Returns
    -------
    vector: tuple
        XYZ components of the resultant vector

    point: tuple
        XYZ coordinates of the location of the resultant vector

    Examples
    --------
    >>> resultant_vector({0 : [ 0.97 , 0.83 , 0.83 ],
                          1 : [ 0.65 , 0.89 , 0.34 ],
                          2 : [ 0.68 , 0.63 , 0.97 ]},
                         {0 : [ 0.97 , 0.83 , 0.83 ],
                          1 : [ 0.65 , 0.89 , 0.34 ],
                          2 : [ 0.68 , 0.63 , 0.97 ]})
    [2.3000000000000003, 2.35, 2.1399999999999997]
    [0.78129727344020572, 0.78043477156745522, 0.7360930822393742],

    """
    points  = []
    weights = []

    for vkey in vectors:
        points.append(vectors[vkey])
        weights.append(length_vector(vectors[vkey]))

    resultant_xyz = weighted_centroid_points(points, weights)
    x, y, z = zip(*vectors.values())
    resultant_vector = [sum(x), sum(y), sum(z)]

    return resultant_vector, resultant_xyz


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   polygons
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def polygon_normal_oriented(polygon, unitized=True):
    """Compute the oriented normal of any closed polygon (can be convex, concave or complex).

    Parameters
    ----------
    polygon : sequence
        The XYZ coordinates of the vertices/corners of the polygon.
        The vertices are assumed to be in order.
        The polygon is assumed to be closed:
        the first and last vertex in the sequence should not be the same.

    Returns
    -------
    list
        The weighted or unitized normal vector of the polygon.

    """
    p = len(polygon)
    assert p > 2, "At least three points required"
    w          = centroid_points(polygon)
    normal_sum = (0, 0, 0)

    for i in range(-1, len(polygon) - 1):
        u          = polygon[i]
        v          = polygon[i + 1]
        uv         = subtract_vectors(v, u)
        vw         = subtract_vectors(w, v)
        normal     = scale_vector(cross_vectors(uv, vw), 0.5)
        normal_sum = add_vectors(normal_sum, normal)

    if not unitized:
        return normal_sum

    return normalize_vector(normal_sum)


def polygon_area_oriented(polygon):
    """Compute the oriented area of a polygon (can be convex or concave).

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
    return length_vector(polygon_normal_oriented(polygon, unitized=False))


def polygon_area_footprint(polygon):
    """Compute the non-oriented area of a polygon (can be convex or concave).

    Parameters
    ----------
    polygon : list of lists
        A list of polygon point coordinates.

    Returns
    -------
    float
        The non-oriented area of the polygon.

    """
    area = 0
    w    = centroid_points(polygon)

    for i in range(-1, len(polygon) - 1):
        u      = polygon[i]
        v      = polygon[i + 1]
        uv     = subtract_vectors(v, u)
        vw     = subtract_vectors(w, v)
        normal = scale_vector(cross_vectors(uv, vw), 0.5)
        area   += length_vector(normal)

    return area


def scale_polygon(polygon, scale):
    """Scale a polygon.

    Parameters
    ----------
    polygon : list of lists
        A list of polygon point coordinates.

    Returns
    -------
    list of lists
        Reordered polygon point coordinates.

    """
    center = centroid_points(polygon)

    scaled_polygon = []

    for pt in polygon:
        vector = subtract_vectors(pt, center)
        new_pt = add_vectors(center, scale_vector(vector, scale))
        scaled_polygon.append(new_pt)

    return scaled_polygon


def untangle_polygon(polygon):
    """Untangle a polygon.

    Parameters
    ----------
    polygon : list of lists
        A list of polygon point coordinates.

    Returns
    -------
    list of lists
        Reordered polygon point coordinates.

    """
    def _cross_edges(edge1, edge2):
        a, b      = edge1
        c, d      = edge2
        edge1_vec = normalize_vector(subtract_vectors(b, a))
        edge2_vec = normalize_vector(subtract_vectors(d, c))
        cross     = cross_vectors(edge1_vec, edge2_vec)
        return cross

    xyz   = {i: polygon[i] for i in range(len(polygon))}
    vkeys = range(len(polygon))

    count = 20
    while count:
        count -= 1
        moved = []

        for i in range(-1, len(polygon) - 1):
            t       = xyz[vkeys[i - 2]]
            u       = xyz[vkeys[i - 1]]
            v       = xyz[vkeys[i]]
            w       = xyz[vkeys[i + 1]]

            u_cross = _cross_edges((t, u), (u, v))
            v_cross = _cross_edges((u, v), (v, w))

            dot = dot_vectors(u_cross, v_cross)

            if dot < 0:
                midpt = midpoint_point_point(u, w)
                vec = scale_vector(subtract_vectors(midpt, v), 1.5)

                xyz[vkeys[i]] = add_vectors(v, vec)
                moved.append([vkeys[i]])

        if len(moved) == 0 :
            break

    return [xyz[i] for i in vkeys]


def polygon_flatness(polygon):
    """Comput the flatness of a polygon.

    Parameters
    ----------
    polygon : list of lists
        A list of polygon point coordinates.

    Returns
    -------
    float
        The flatness.

    Note
    ----
    compas.geometry.mesh_flatness function currently only works for quadrilateral faces.
    This function uses the distance between each face vertex and its projected point on the best-fit plane of the face as the flatness metric.

    """
    deviation = 0

    plane     = bestfit_plane(polygon)

    for pt in polygon:
        pt_proj = project_point_plane(pt, plane)
        dev     = distance_point_point(pt, pt_proj)
        if dev > deviation:
            deviation = dev

    return deviation


def is_polygon_self_intersecting(polygon):
    """Computes if as polygon is self intersecting in plane, or self overlapping in space.

    Parameters
    ----------
    polygon : list of lists
        A list of polygon point coordinates.

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
    for i in range(-1, len(polygon) - 1):
        edges.append((i, i + 1))

    for u1, v1 in edges:
        for u2, v2 in edges:
            if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                continue
            else:
                a = polygon[u1]
                b = polygon[v1]
                c = polygon[u2]
                d = polygon[v2]

                int_1, int_2 = intersection_line_line((a, b), (c, d))

                if int_1 or int_2:
                    if distance_point_point(int_1, int_2) > 0:
                        overlapping = True
                    if is_point_on_segment(int_1, (a, b)) or is_point_on_segment(int_2, (c, d)):
                            intersecting = True

    return overlapping, intersecting

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   mesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_face_flatness(cell):
    """Compute the flatness of every face of a mesh.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.

    Returns
    -------
    dict
        A dictionary of flatness deviation for every face of the mesh.

    """

    flatness_dict = {fkey : 0 for fkey in cell.face}

    for fkey in cell.face:
        f_vkeys = cell.face_vertices(fkey)
        f_pts   = [cell.vertex_coordinates(vkey) for vkey in f_vkeys]
        dev     = polygon_flatness(f_pts)

        flatness_dict[fkey] = dev

    return flatness_dict


def cell_face_areaness(cell, target_areas):
    """Compute the areaness of every face of a mesh.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    target_areas : dict
        Dictionary of target areas.

    Returns
    -------
    dict
        A dictionary of area deviation for each face of the mesh.

    """
    areaness_dict = {}

    for fkey in target_areas:
        area = cell.face_area(fkey)
        areaness_dict[fkey] = abs(target_areas[fkey] - area)

    return areaness_dict


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
    """Compute the flatness of every face of a volmesh.

    Parameters
    ----------
    volmesh : volmesh object

    Returns
    -------
    dict
        A dictionary of flatness deviation for every face of the volmesh.

    """
    flatness_dict = {fkey : 0 for fkey in volmesh.faces()}

    for fkey in volmesh.faces():
        f_vkeys = volmesh.halfface_vertices(fkey)
        f_pts   = [volmesh.vertex_coordinates(vkey) for vkey in f_vkeys]
        dev     = polygon_flatness(f_pts)

        flatness_dict[fkey] = dev

    return flatness_dict


def volmesh_face_areaness(volmesh, target_areas):
    """Compute the areaness of every face of a volmesh.

    Parameters
    ----------
    volmesh : volmesh object

    Returns
    -------
    dict
        A dictionary of area deviation for each face of the volmesh.

    """
    areaness_dict = {}

    for hfkey in target_areas:
        area = volmesh.halfface_oriented_area(hfkey)
        areaness_dict[hfkey] = abs(target_areas[hfkey] - area)

    return areaness_dict


def _get_current_volmesh_normals(volmesh):
    normal_dict = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_oriented_normal(hfkey)
        normal_dict[hfkey] = {'normal': normal, 'center': center}
    return normal_dict


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
    """Compute the centroid of the datastructure.

    Parameters
    ----------
    datastructure
        A network, mesh or volmesh object.

    Returns
    -------
    list
        The coordinates of the centroid.

    """
    points = [datastructure.vertex_coordinates(vkey) for vkey in datastructure.vertex]

    return centroid_points(points)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
