from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs

from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
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

from compas.utilities import geometric_key

from compas_rhino.utilities import draw_labels
from compas_rhino.utilities import draw_lines
from compas_rhino.utilities import draw_faces


def oriented_normal_polygon(points):
    """Computes the oriented normal of the polygon, with self-intersections taken into account.

    Parameters:
        points (sequence): A sequence of points.

    Returns:
        list: The oriented normal vector (NOT unitised).

    Notes:
        The points in the list should be unique. For example, the first and last
        point in the list should not be the same.

        Length of this normal vector is then the oriented area of the polygon.
    """

    def _cross_edges(edge1, edge2):
        a, b      = edge1
        c, d      = edge2
        edge1_vec = normalize_vector(subtract_vectors(b, a))
        edge2_vec = normalize_vector(subtract_vectors(d, c))
        cross     = cross_vectors(edge1_vec, edge2_vec)
        return cross

    intersection = False

    # ==========================================================================
    #   0. initialize polygon
    # ==========================================================================
    # dict of all vertex keys and coordinates ----------------------------------
    xyz = {i: points[i] for i in range(len(points))}

    # get initial vertex keys, edges, and vertex orientations ------------------
    init_vkeys = range(len(points))
    init_edges = []
    init_cross = {}
    for i in range(-1, len(points) - 1):
        init_edges.append([init_vkeys[i], init_vkeys[i + 1]])
        u     = xyz[init_vkeys[i - 1]]
        v     = xyz[init_vkeys[i]]
        w     = xyz[init_vkeys[i + 1]]
        cross = _cross_edges((u, v), (v, w))
        init_cross[init_vkeys[i]] = cross

    # store all eventual intersections on the initial edges --------------------
    edge_ints = {}
    for i in range(-1, len(points) - 1):
        u            = init_vkeys[i]
        v            = init_vkeys[i + 1]
        edge_ints[u] = {v: [u, v]}

    # ==========================================================================
    #   1. split edges and find intersection
    # ==========================================================================
    int_geokeys = {}
    seen_edge_pairs = set()
    for u1, v1 in init_edges:
        for u2, v2 in init_edges:

            edge_pair = frozenset([u1, v1, u2, v2])

            # skip if, the two lines have already been intersected -------------
            if edge_pair in seen_edge_pairs:  # already seen
                continue
            # skip if the two edges are consectuive ----------------------------
            elif u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
                seen_edge_pairs.add(edge_pair)
                continue

            else:
                a = xyz[u1]
                b = xyz[v1]
                c = xyz[u2]
                d = xyz[v2]
                int_1, int_2 = intersection_line_line((a, b), (c, d))
                if int_1 or int_2:
                    if distance(int_1, int_2) > 0.1:
                        print('The polygon is gauche: self-overlapping, but not self-intersecting.')
                        return
                    if is_point_on_segment(int_1, (a, b), tol=0.001) and is_point_on_segment(int_2, (c, d), tol=0.001):

                        intersection = True

                        geokey       = geometric_key(int_1)

                        if geokey not in int_geokeys:
                            new_vkey = max(xyz.keys()) + 1
                            int_geokeys[geokey] = new_vkey

                        new_vkey      = int_geokeys[geokey]
                        xyz[new_vkey] = int_1

                        if new_vkey not in edge_ints[u1][v1]:
                            edge_ints[u1][v1].append(new_vkey)
                        if new_vkey not in edge_ints[u2][v2]:
                            edge_ints[u2][v2].append(new_vkey)

                seen_edge_pairs.add(edge_pair)

    if not intersection:
        print('-------------------------------------------------------------------')
        print('.')
        print('The polygon is NOT self-intersecting --- the area is:', area_polygon(points))
        print('.')
        print('-------------------------------------------------------------------')
        return

    # ==========================================================================
    #   2. reorder intersections along each edge
    # ==========================================================================
    split_edges = {}
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
            if a not in init_cross:
                init_cross[a] = init_cross[u]

    # ==========================================================================
    #   3. construct sub-faces
    # ==========================================================================
    subpolygons = []

    seen_edges = set()
    for u0 in xyz.keys():
        for v0 in split_edges[u0]:
            if (u0, v0) not in seen_edges:
                subface = [u0, v0]

                count = 100
                while count:
                    count  -= 1
                    u      = subface[-2]
                    v      = subface[-1]
                    w_list = split_edges[v].keys()

                    # break if initial vertex is in the w_list...
                    # this means that the subface has been found...
                    if subface[0] in w_list:
                        break

                    if len(w_list) == 1:
                        subface.append(w_list[0])
                        continue

                    # sort w's -------------------------------------------------
                    conv_list = {}
                    conc_list = {}
                    for w in w_list:
                        if (v, w) not in seen_edges:
                            a             = xyz[u]
                            b             = xyz[v]
                            c             = xyz[w]
                            orientation   = init_cross[u0]
                            uvw_cross     = _cross_edges((a, b), (b, c))
                            dot           = dot_vectors(orientation, uvw_cross)
                            uvw_cross_amp = length_vector(uvw_cross)
                            # try to pick w's with the same normal direction...
                            # and ignore consecutive edges...
                            if uvw_cross_amp > 0.001:
                                if dot > 0:
                                    conv_list[w] = uvw_cross_amp
                                if dot < 0:
                                    conc_list[w] = uvw_cross_amp
                    sorted_conv_w = sorted(conv_list, key=conv_list.get)
                    sorted_conc_w = sorted(conc_list, key=conc_list.get)
                    sorted_w      = sorted_conv_w + sorted_conc_w

                    # add w to subface -----------------------------------------
                    for next_w in sorted_w:
                        if next_w not in subface[1:]:
                            subface.append(next_w)
                            break

                # add subface --------------------------------------------------
                for i in range(-1, len(subface) - 1):
                    seen = (subface[i], subface[i + 1])
                    seen_edges.add(seen)

                subpolygons.append(subface)

    # ==========================================================================
    #   4. compute normals and draw
    # ==========================================================================
    normal_sum   = (0, 0, 0)
    for polygon in subpolygons:
        pts        = [xyz[vkey] for vkey in polygon]
        area       = area_polygon(pts)
        normal     = scale_vector(normal_polygon(pts), area)
        normal_sum = add_vectors(normal_sum, normal)

    # ==========================================================================
    #   5. drawing (for this gist only)
    # ==========================================================================
    scale = 3

    # directed split edges as arrows -------------------------------------------
    edges        = []
    for u in split_edges:
        for v in split_edges[u]:
            edges.append({
                'start': xyz[u],
                'end'  : xyz[v],
                'arrow': 'end',
                'color': (0, 0, 0),
                'name' : '{}-{}.from.{}'.format(u, v, split_edges[u][v])})

    # vertex labels ------------------------------------------------------------
    labels       = []
    for key, location in iter(xyz.items()):
        color = (0, 0, 0)
        if key not in init_vkeys:
            color = (255, 255, 255)
        labels.append({'pos'  : location,
                       'name' : str(key),
                       'color': color,
                       'text' : str(key)})

    # subfaces and subface normals ---------------------------------------------
    faces        = []
    normal_lines = []
    normal_sum   = (0, 0, 0)
    for polygon in subpolygons:
        pts        = [xyz[vkey] for vkey in polygon]
        area       = area_polygon(pts)
        normal     = scale_vector(normal_polygon(pts), area)
        normal_sum = add_vectors(normal_sum, normal)
        center     = centroid_points(pts)
        color      = (0, 0, 255)
        normal     = normalize_vector(normal)
        if normal[2] < 0:
            color = (255, 0, 0)
        normal_lines.append({
            'start': center,
            'end'  : add_vectors(center, scale_vector(normal, scale)),
            'arrow': 'end',
            'color': color,
            'name' : 'polygon:{}'.format(polygon, length_vector(normal))})
        faces.append({
            'points': pts,
            'color' : color,
            'name' : 'polygon:{}'.format(polygon)})

    # vertex normals -----------------------------------------------------------
    for vkey in init_cross:
        normal = normalize_vector(init_cross[vkey])
        factor = 0.3 * scale
        color = (0, 127, 0)
        if vkey in init_vkeys:
            factor = 0.6 * scale
            color = (0, 255, 0)
        normal_lines.append({
            'start': xyz[vkey],
            'end'  : add_vectors(xyz[vkey], scale_vector(normal, factor)),
            'arrow': 'end',
            'color': color})

    # global polygon normal ----------------------------------------------------
    g_center = centroid_points([xyz[vkey] for vkey in xyz])
    global_normal = normalize_vector(normal_sum)
    normal_lines.append({
        'start': g_center,
        'end'  : add_vectors(g_center, scale_vector(global_normal, scale * 3)),
        'arrow': 'end',
        'color': (255, 255, 0),
        'name' : 'area:{}'.format(length_vector(normal_sum))})

    draw_lines(edges)
    draw_lines(normal_lines)
    draw_faces(faces)
    draw_labels(labels)

    # ==========================================================================
    #   6. return oriented normal of the polygon
    # ==========================================================================

    return normal_sum


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
    result        = oriented_normal_polygon(points)
    oriented_area = length_vector(result)

    print('-------------------------------------------------------------------')
    print('.')
    print('.   The polygon is self-intersecting --- and the area is:', oriented_area)
    print('.')
    print('-------------------------------------------------------------------')
