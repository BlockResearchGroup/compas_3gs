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

from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_faces


def oriented_normal_polygon(points):
    """Computes the oriented normal of the polygon, with self-intersections taken into account.

    Parameters:
        points (sequence): A sequence of points.

    Returns:
        list: The oriented normal vector.

    Notes:
        The points in the list should be unique. For example, the first and last
        point in the list should not be the same.

    Warning:
        This does not work for some cases; even-odd rule must hold true.
        This may be directly related to the number of vertices vs the number of possible enclosures.
        This can probably be proven mathematically...

    """

    def _cross_edges(edge1, edge2):
        a, b      = edge1
        c, d      = edge2
        edge1_vec = normalize_vector(subtract_vectors(b, a))
        edge2_vec = normalize_vector(subtract_vectors(d, c))
        cross     = cross_vectors(edge1_vec, edge2_vec)
        return cross

    intersection = False

    # initialize the list of points, and get initial edges ---------------------
    xyz        = {i: points[i] for i in range(len(points))}

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


    int_geokeys = {}
    edge_ints   = {}

    for i in range(-1, len(points) - 1):
        u = init_vkeys[i]
        v = init_vkeys[i + 1]
        edge_ints[u] = {v: [u, v]}






    added_vkeys = []


    # ==========================================================================
    #   1. split edges and find intersection
    # ==========================================================================


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
                        print('The polygon is self-overlapping.')
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


    print(int_geokeys)

    if not intersection:
        print('The polygon is NOT self-intersecting --- the area is:', area_polygon(points))
        return

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




    # split edges --------------------------------------------------------------
    lines        = []
    for u in split_edges:
        for v in split_edges[u]:
            lines.append({
                'start': xyz[u],
                'end'  : xyz[v],
                'arrow': 'end',
                'color': (0, 0, 0),
                'name' : '{}-{}.from.{}'.format(u, v, split_edges[u][v])})
    xdraw_lines(lines)

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
    xdraw_labels(labels)


    print(split_edges)
    print(all_edge_list)

    print(init_vkeys + int_geokeys.values())
    # ==========================================================================
    #   3. construct sub-faces
    # ==========================================================================
    subpolygons = []

    seen_edges = set()
    for u0 in init_vkeys:
        for v0 in split_edges[u0]:
            if frozenset([u0, v0]) not in seen_edges:
                print('-------------------------------------------------------')
                print('-------------------------------------------------------')
                print('-------------------------------------------------------')

                subface = [u0, v0]
                count = 50
                while count:
                    print('COUNT', count, '-----------------------------------')
                    count  -= 1
                    u      = subface[-2]
                    v      = subface[-1]
                    w_list = split_edges[v].keys()

                    print('U V :', u, v)
                    print('w_list', w_list)

                    conv_list = {}
                    conc_list = {}
                    if len(w_list) == 1:
                        subface.append(w_list[0])

                    else:
                        # order w's ------------------------------------------------
                        for w in w_list:
                            if frozenset([v, w]) not in seen_edges:
                                if w == subface[0]:
                                    break
                                if (v, w) not in seen_edges:
                                    if w not in subface:
                                        subface.append(w)
                                        break

                    #     # ancestor_prev = split_edges[u][v]
                    #     # ancestor_curr = split_edges[v][w]

                    #     # if ancestor_prev == ancestor_curr:

                    #     # if ancestor_prev != ancestor_curr:
                    #     a = xyz[u]
                    #     b = xyz[v]
                    #     c = xyz[w]
                    #     ancestor_cross = init_cross[u0]
                    #     uvw_cross      = _cross_edges((a, b), (b, c))
                    #     dot = dot_vectors(ancestor_cross, uvw_cross)
                    #     # only pick w's with the same normal direction
                    #     if dot > 0:
                    #         conv_list[w] = length_vector(uvw_cross)
                    #     if dot == 0:
                    #         descendent_vertex = w
                    #     if dot < 0:
                    #         conc_list[w] = length_vector(uvw_cross)
                    # sorted_conv_w = sorted(conv_list, key=conv_list.get)
                    # sorted_conc_w = sorted(conc_list, key=conc_list.get)
                    # sorted_w = sorted_conv_w + [descendent_vertex] + sorted_conc_w

                    # print('sorted_w', sorted_w)

                    # for next_w in sorted_w:
                    #     if frozenset([v, next_w]) not in seen_edges:

                    #         if next_w == subface[0]:
                    #             break

                    #         if next_w in subface[1:]:
                    #             print(next_w, 'ADDED')
                    #             subface.append(next_w)
                    #             break


                for i in range(-1, len(subface) - 1):
                    seen = frozenset([subface[i], subface[i + 1]])
                    seen_edges.add(seen)

                print(seen_edges)
                print('subface', subface)
                subpolygons.append(subface)



    # seen_edges = set()
    # for edge in all_edge_list:
    #     print('------------------------------------------------------------')
    #     u0 = edge[0]
    #     v0 = edge[1]
    #     print('edge', u0, v0)
    #     if frozenset([u0, v0]) not in seen_edges:
    #         subface = [u0, v0]

    #         count = 10
    #         while count:
    #             count -= 1
    #             u = subface[-2]
    #             v = subface[-1]
    #             w_list = split_edges[v].keys()
    #             print(w_list)
    #             for w in w_list:

    #                 if frozenset([v, w]) not in seen_edges:
    #                     print(v, w, 'not seen')
    #                     if w not in subface[1:]:
    #                         print( w, 'not yet in subface')
    #                         subface.append(w)
    #                         break

    #         for i in range(-1, len(subface) - 1):
    #             seen = frozenset([subface[i], subface[i + 1]])
    #             seen_edges.add(seen)

    #         print('subface', subface)
    #         subpolygons.append(subface)






    # seen_edges = set()
    # for u0 in init_vkeys:
    #     for v0 in split_edges[u0]:
    #         if frozenset([u0, v0]) not in seen_edges:
    #             subface = [u0, v0]
    #             print('---------------------------------------------------')

    #             count = 10
    #             while count:
    #                 count -= 1
    #                 u = subface[-2]
    #                 v = subface[-1]
    #                 w_list = split_edges[v].keys()
    #                 print('subface', subface)
    #                 print('w_list', w_list)
    #                 # for w in w_list:

    #                 #     if w == subface[0]:
    #                 #         break

    #                 #     if w not in subface[1:]:
    #                 #         if frozenset([v, w]) not in seen_edges:
    #                 #             subface.append(w)
    #                 #             break

    #                 if len(w_list) == 1:  # means concave subface
    #                     if w_list[0] == subface[0]:
    #                         break
    #                     subface.append(w_list[0])
    #                     continue

    #                 cross_list = {}

    #                 for w in w_list:
    #                     ancestor_prev = split_edges[u][v]
    #                     ancestor_curr = split_edges[v][w]


    #                     if ancestor_prev == ancestor_curr:
    #                         descendent_vertex = w
    #                     if ancestor_prev != ancestor_curr:
    #                         a = xyz[u]
    #                         b = xyz[v]
    #                         c = xyz[w]
    #                         ancestor_cross = init_cross[u0]
    #                         uvw_cross      = _cross_edges((a, b), (b, c))
    #                         dot = dot_vectors(ancestor_cross, uvw_cross)
    #                         # if dot > 0:
    #                         cross_list[w] = length_vector(uvw_cross)
    #                 sorted_w = sorted(cross_list, key=cross_list.get)
    #                 print('sorted_w', sorted_w)



    #                 if len(sorted_w) == 0:
    #                     next_key = descendent_vertex
    #                 else:
    #                     next_key = sorted_w[0]


    #                 if next_key in subface[1:]:
    #                     next_key = descendent_vertex

    #                 print('next_key', next_key)

    #                 if next_key == subface[0]:
    #                     break
    #                 if frozenset([v, next_key]) not in seen_edges:
    #                     subface.append(next_key)




    #             # print('final subface', subface)
    #             for i in range(-1, len(subface) - 1):
    #                 seen = frozenset([subface[i], subface[i + 1]])
    #                 seen_edges.add(seen)

    #             subpolygons.append(subface)






    for item in subpolygons:
        print('subpolygon', item)

    # ==========================================================================
    #   4. compute normals and draw
    # ==========================================================================
    normal_sum   = (0, 0, 0)

    for polygon in subpolygons:
        pts        = [xyz[vkey] for vkey in polygon]
        area       = area_polygon(pts)
        normal     = scale_vector(normal_polygon(pts), area)
        normal_sum = add_vectors(normal_sum, normal)

    oriented_area = length_vector(normal_sum)

    print('-------------------------------------------------------------------')
    print('.')
    print('.   The polygon is self-intersecting --- and the area is:', oriented_area)
    print('.')
    print('-------------------------------------------------------------------')

    # ==========================================================================
    #   5. drawing
    # ==========================================================================
    scale = 0.15


    # faces and normals --------------------------------------------------------
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

    g_center = centroid_points([xyz[vkey] for vkey in xyz])
    normal_lines.append({
        'start': g_center,
        'end'  : add_vectors(g_center, scale_vector(normal_sum, scale)),
        'arrow': 'end',
        'color': (255, 255, 0),
        'name' : 'area:{}'.format(length_vector(normal_sum))})
    xdraw_faces(faces)

    # vertex normals -----------------------------------------------------------
    for vkey in init_cross:
        normal = scale_vector(init_cross[vkey], 10)
        normal_lines.append({
            'start': xyz[vkey],
            'end'  : add_vectors(xyz[vkey], scale_vector(normal, 0.5)),
            'arrow': 'end',
            'color': (0, 255, 0)})
    xdraw_lines(normal_lines)


    return normal_sum


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    guid = rs.GetObject("select polysurfaces", filter=4)

    rs.HideObjects(guid)

    if not rs.IsCurveClosed(guid):
        print('not a closed polyline')

    points = [[pt.X, pt.Y, pt.Z] for pt in rs.PolylineVertices(guid)]
    points = points[:-1]

    result = oriented_normal_polygon(points)
