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




def oriented_normal_polygon(points, unitized=True):
    """Computes the oriented normal of the polygon, with self-intersections taken into account.

    Parameters:
        points (sequence): A sequence of points.

    Returns:
        list: The oriented normal vector.

    Notes:
        The points in the list should be unique. For example, the first and last
        point in the list should not be the same.

    Warning:
        This does not work for some cases...

    """

    def _cross_edges(edge1, edge2):
        a, b = edge1
        c, d = edge2
        edge1_vec = normalize_vector(subtract_vectors(b, a))
        edge2_vec = normalize_vector(subtract_vectors(d, c))
        cross = cross_vectors(edge1_vec, edge2_vec)
        return cross


    intersection = False


    # initialize the list of points, and get initial edges ---------------------
    xyz        = {i: points[i] for i in range(len(points))}

    init_vkeys = range(len(points))
    init_edges = []
    init_cross = {}

    for i in range(-1, len(points) - 1):
        init_edges.append([init_vkeys[i], init_vkeys[i + 1]])
        u = xyz[init_vkeys[i - 1]]
        v = xyz[init_vkeys[i]]
        w = xyz[init_vkeys[i + 1]]
        cross = _cross_edges((u, v), (v, w))
        init_cross[init_vkeys[i]] = cross


    # label initial points -----------------------------------------------------
    labels = []
    for key, location in iter(xyz.items()):
        labels.append({'pos'  : location,
                       'name' : str(key),
                       'color': (0, 0, 0),
                       'text' : str(key)})
    xdraw_labels(labels)


    # ==========================================================================
    #   1. split edges and find intersection
    # ==========================================================================
    int_geokeys = {}
    edge_ints = {}
    for i in range(-1, len(points) - 1):
        u = init_vkeys[i]
        v = init_vkeys[i + 1]
        edge_ints[u] = {v: [u, v]}

    seen_edge_pairs = set()
    for u1, v1 in init_edges:
        for u2, v2 in init_edges:

            edge_pair = frozenset([u1, v1, u2, v2])

            # skip if, the two lines are ... -----------------------------------
            if edge_pair in seen_edge_pairs:  # already seen
                continue

            elif u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:  # consecutive
                seen_edge_pairs.add(edge_pair)
                continue
            # ------------------------------------------------------------------

            else:
                seen_edge_pairs.add(edge_pair)

                a = xyz[u1]
                b = xyz[v1]
                c = xyz[u2]
                d = xyz[v2]

                int_1, int_2 = intersection_line_line((a, b), (c, d))

                if int_1 or int_2:

                    if distance(int_1, int_2) > 0.1:
                        print('-------------------------------------------------------------------')
                        print('.')
                        print('.   The Polygon is self-overlapping.')
                        print('.')
                        print('-------------------------------------------------------------------')
                        return

                    if is_point_on_segment(int_1, (a, b), tol=0.001) and is_point_on_segment(int_2, (c, d), tol=0.001):

                        geokey = geometric_key(int_1)

                        if geokey not in int_geokeys:
                            new_vkey = max(xyz.keys()) + 1
                            int_geokeys[geokey] = new_vkey

                        new_vkey = int_geokeys[geokey]

                        xyz[new_vkey] = int_1
                        intersection = True

                        if new_vkey not in edge_ints[u1][v1]:
                            edge_ints[u1][v1].append(new_vkey)
                        if new_vkey not in edge_ints[u2][v2]:
                            edge_ints[u2][v2].append(new_vkey)


    if not intersection:
        print('-------------------------------------------------------------------')
        print('.')
        print('.   The polygon is NOT self-intersecting --- the area is:', area_polygon(points))
        print('.')
        print('-------------------------------------------------------------------')
        return

    # label intersection points ------------------------------------------------
    int_labels = []
    for key, location in iter(xyz.items()):
        if key not in init_vkeys:
            int_labels.append({'pos'  : location,
                               'name' : str(key),
                               'color': (255, 255, 255),
                               'text' : str(key)})
    xdraw_labels(int_labels)


    # ==========================================================================
    #   2. reorder intersections along each edge
    # ==========================================================================
    split_edges = {}
    all_edge_list = []
    for u in edge_ints:
        for v in edge_ints[u]:
            vkeys   = edge_ints[u][v]
            dist    = [distance(xyz[u], xyz[vkey]) for vkey in vkeys]
            ordered = [vkey for dist, vkey in sorted(zip(dist, vkeys))]
        for i in range(len(ordered) - 1):
            a = ordered[i]
            b = ordered[i + 1]
            if a not in split_edges:  # store u us the ancestor point
                split_edges[a] = {}

            split_edges[a][b] = u
            all_edge_list.append((a, b))


    # draw edges arrows --------------------------------------------------------
    lines = []
    for u in split_edges:
        for v in split_edges[u]:
            lines.append({
                'start': xyz[u],
                'end'  : xyz[v],
                'arrow': 'end',
                'color': (0, 0, 0),
                'name' : '{}-{}.from.{}'.format(u, v, split_edges[u][v])})
    xdraw_lines(lines)
    # --------------------------------------------------------------------------



    # ==========================================================================
    #   3. construct sub-faces
    # ==========================================================================

    subpolygons = []

    seen_edges = set()

    # while len(seen_edges) != len(all_edge_list):
    for u0 in init_vkeys:

        for v0 in split_edges[u0]:

            if frozenset([u0, v0]) not in seen_edges:

                subface = [u0, v0]

                count = 10
                while count:
                    count -= 1

                    u = subface[-2]
                    v = subface[-1]

                    w_list = split_edges[v].keys()

                    if len(w_list) == 1:  # means concave subface
                        subface.append(w_list[0])
                        break

                    cross_list = {}

                    for w in w_list:

                        ancestor_prev = split_edges[u][v]
                        ancestor_curr = split_edges[v][w]

                        if ancestor_prev != ancestor_curr:

                            a = xyz[u]
                            b = xyz[v]
                            c = xyz[w]

                            ancestor_cross = init_cross[u0]
                            uvw_cross      = _cross_edges((a, b), (b, c))
                            dot = dot_vectors(ancestor_cross, uvw_cross)

                            if dot > 0:
                                cross_list[w] = length_vector(uvw_cross)

                    w = sorted(cross_list, key=cross_list.get)[0]

                    if w == subface[0]:
                        break

                    subface.append(w)


                for i in range(-1, len(subface) - 1):
                    seen = frozenset([subface[i], subface[i + 1]])
                    seen_edges.add(seen)

                subpolygons.append(subface)


    # ==========================================================================
    #   4. compute normals
    # ==========================================================================

    scale = 0.25

    faces = []
    normal_lines = []
    normal_sum = (0, 0, 0)

    for polygon in subpolygons:
        pts = [xyz[vkey] for vkey in polygon]
        area = area_polygon(pts)
        normal = scale_vector(normal_polygon(pts), area)
        normal_sum = add_vectors(normal_sum, normal)
        center = centroid_points(pts)
        color = (0, 0,255)
        if normal[2] < 0:
            color = (255, 0, 0)
        normal_lines.append({
            'start': center,
            'end'  : add_vectors(center, scale_vector(normal, 0.25)),
            'arrow': 'end',
            'color': color,
            'name' : 'polygon:{}_area:{}'.format(polygon, length_vector(normal))
        })
        faces.append({
            'points': pts,
            'color' : color,
            'name' : 'polygon:{}'.format(polygon)})


    global_centroid = centroid_points([xyz[vkey] for vkey in xyz])
    normal_lines.append({
            'start': global_centroid,
            'end'  : add_vectors(global_centroid, scale_vector(normal_sum, scale)),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name' : 'area:{}'.format(length_vector(normal_sum))
        })

    xdraw_lines(normal_lines)
    xdraw_faces(faces)








    print('-------------------------------------------------------------------')
    print('.')
    print('.   The polygon is self-intersecting --- and the area is:', length_vector(normal_sum))
    print('.')
    print('-------------------------------------------------------------------')









def oriented_area_polygon(points):
    """Computes the oriented area of a polygon, with self-intersections taken into account.

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
        The oriented area of the polygon.

    """

    index = []
    network = Network()
    for i, (x, y, z) in enumerate(vertices):
        network.add_vertex(i, x=x, y=y, z=z)
        index.append(i)
    for i in range(0, len(points)):
        network.add_edge(i, i + 1)
