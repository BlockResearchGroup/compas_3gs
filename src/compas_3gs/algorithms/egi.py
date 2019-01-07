from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import Network

from compas.geometry import add_vectors
from compas.geometry import distance_point_point as distance
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors
from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors

from compas.topology.duality import _find_first_neighbor

from compas.utilities.maps import geometric_key

from compas_3gs.diagrams import EGI
from compas_3gs.diagrams import Cell

try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    from Rhino.Geometry import Arc
    from Rhino.Geometry import Point3d
    from Rhino.Geometry import ArcCurve
    from Rhino.Geometry import Vector3d
    from Rhino.Geometry import Circle
    from Rhino.Geometry import Plane

    from Rhino.Geometry.Intersect.Intersection import CurveCurve as CCX

except ImportError:
    compas.raise_if_ironpython()


__all__ = [
    'egi_from_vectors',
    'unit_polyhedron'
]


def egi_from_vectors(vectordict, origin, tol=0.001):
    """

    warnings:
        dependent on rhino arc function...


    exceptions:
        1. normals pointing in the same direction
        2. parallel loads

    """

    egi = Network()

    # --------------------------------------------------------------------------
    #   1. add vertices from vectors
    # --------------------------------------------------------------------------
    vertex_geokeys = {}

    for vkey in vectordict:
        normal     = normalize_vector(vectordict[vkey])
        vertex_xyz = add_vectors(normal, origin)
        vertex_geokeys[geometric_key(normal)] = vkey
        egi.add_vertex(x=vertex_xyz[0],
                       y=vertex_xyz[1],
                       z=vertex_xyz[2],
                       key=vkey,
                       attr_dict={'type'  : 'face',
                                  'normal': normal,
                                  'nbrs'  : []})

    # --------------------------------------------------------------------------
    #   2.  Identify main adjacencies
    # --------------------------------------------------------------------------
    vkey_pairs = set()

    for vkey in egi.vertex:
        v_crs_dict = {}

        for nbr_vkey in egi.vertex:

            if nbr_vkey is not vkey:

                n1 = egi.vertex[vkey]['normal']
                n2 = egi.vertex[nbr_vkey]['normal']

                # This checks if the normals are opposite ----------------------
                dot = dot_vectors(n1, n2)

                if dot > 1 - tol:
                    raise Exception("Coincident vectors detected.")

                elif dot > -1 + tol:

                    this_crs = cross_vectors(n1, n2)
                    unit_crs = normalize_vector(this_crs)

                    crs_gkey = geometric_key(unit_crs)

                    # Check to see if any other normals are coplanar
                    if crs_gkey not in v_crs_dict:
                        v_crs_dict[crs_gkey] = nbr_vkey

                    # If multiple arcs are coplanar, choose the closer one
                    elif crs_gkey in v_crs_dict:
                        this_dist = distance(egi.vertex_coordinates(vkey),
                                             egi.vertex_coordinates(nbr_vkey))
                        test_dist = distance(egi.vertex_coordinates(vkey),
                                             egi.vertex_coordinates(v_crs_dict[crs_gkey]))
                        if this_dist < test_dist:
                            del v_crs_dict[crs_gkey]
                            v_crs_dict[crs_gkey] = nbr_vkey

        # Add to overall connectivity dict -------------------------------------
        for crs_gkey in v_crs_dict:
            nbr_vkey = v_crs_dict[crs_gkey]
            pair     = frozenset([vkey, nbr_vkey])
            vkey_pairs.add(pair)

    # --------------------------------------------------------------------------
    #   3.  Main adjacency arcs
    # --------------------------------------------------------------------------
    arcs = {}

    for pair in vkey_pairs:
        u, v = list(pair)
        arc  = _draw_arc(egi.vertex[u]['normal'],
                         egi.vertex[v]['normal'],
                         origin)

        if len(arcs) == 0:
            arc_key = 0
        else:
            arc_key = max(int(x) for x in arcs.keys()) + 1
        arcs[arc_key] = {'arc'      : arc,
                         'vkeys'    : [u, v],
                         'end_vkeys': [u, v],
                         'int_vkeys': {}, }

    # --------------------------------------------------------------------------
    #   3.  arc intersections --> cross adjacencies
    # --------------------------------------------------------------------------
    arc_pairs_seen = set()
    for arckey_1 in arcs:
        for arckey_2 in arcs:
            if arckey_1 != arckey_2:
                arc_pair = frozenset([arckey_1, arckey_2])
                if arc_pair not in arc_pairs_seen:
                    arc_1 = arcs[arckey_1]['arc']
                    arc_2 = arcs[arckey_2]['arc']
                    intersection = _curve_curve_intx(arc_1, arc_2)
                    if intersection:
                        new_vkey   = max(int(vkey) for vkey in egi.vertex.keys()) + 1
                        new_normal = subtract_vectors(intersection, origin)
                        new_normal = normalize_vector(new_normal)
                        new_vertex_geokey = geometric_key(new_normal, precision='3f')

                        # if intersection is not an endpoint -------------------
                        if new_vertex_geokey not in vertex_geokeys.keys():
                            vertex_geokeys[new_vertex_geokey] = new_vkey
                            egi.add_vertex(x=intersection[0],
                                           y=intersection[1],
                                           z=intersection[2],
                                           key=new_vkey,
                                           attr_dict={'type'      : 'zero',
                                                      'normal'    : new_normal,
                                                      'magnitude' : 0,
                                                      'nbrs'      : []})
                            arcs[arckey_1]['vkeys'].append(new_vkey)
                            arcs[arckey_2]['vkeys'].append(new_vkey)
                            arcs[arckey_1]['int_vkeys'][new_vkey] = arckey_2
                            arcs[arckey_2]['int_vkeys'][new_vkey] = arckey_1

                        # if intersection already exists -----------------------
                        elif new_vertex_geokey in vertex_geokeys.keys():
                            vkey = vertex_geokeys[new_vertex_geokey]
                            if vkey not in arcs[arckey_1]['vkeys']:
                                arcs[arckey_1]['vkeys'].append(vkey)
                                arcs[arckey_1]['int_vkeys'][vkey] = arckey_2
                            if vkey not in arcs[arckey_2]['vkeys']:
                                arcs[arckey_2]['vkeys'].append(vkey)
                                arcs[arckey_2]['int_vkeys'][vkey] = arckey_1
                        arc_pairs_seen.add(arc_pair)

    # --------------------------------------------------------------------------
    #   5.  Reorder vertices along each arc and add edges to EGI network
    # --------------------------------------------------------------------------
    for arckey in arcs:
        vkeys = arcs[arckey]['vkeys']
        if len(vkeys) > 2:
            pt_list = [egi.vertex_coordinates(key) for key in vkeys]
            arcs[arckey]['vkeys'] = _reorder_pts_on_arc(pt_list,
                                                        arcs[arckey]['vkeys'],
                                                        arcs[arckey]['arc'])[1]
            edge_type = 'cross'
        else:
            edge_type = 'main'
        for i in range(len(arcs[arckey]['vkeys']) - 1):
            vkey_1 = arcs[arckey]['vkeys'][i]
            vkey_2 = arcs[arckey]['vkeys'][i + 1]
            egi.vertex[vkey_1]['nbrs'] += [vkey_2]
            egi.vertex[vkey_2]['nbrs'] += [vkey_1]
            egi.add_edge(vkey_1, vkey_2)
            # egi.edge[vkey_1][vkey_2] = {'type' : edge_type}

    # --------------------------------------------------------------------------
    #   6.  For each vertex, sort nbrs in ccw order
    # --------------------------------------------------------------------------
    _egi_sort_v_nbrs(egi)

    # --------------------------------------------------------------------------
    #   7.  Add EGI Network faces
    # --------------------------------------------------------------------------
    egi_mesh = EGI()
    for vkey in egi.vertex:
        egi_mesh.vertex[vkey] = egi.vertex[vkey]

    _egi_find_faces(egi, egi_mesh)

    return egi_mesh


def unit_polyhedron(egi):

    cell        = Cell()
    cell.name   = 'cell'

    for fkey in egi.face:
        x, y, z = egi.face_center(fkey)
        cell.add_vertex(key=fkey, x=x, y=y, z=z)

    for vkey in egi.vertex:
        cell_face = egi.vertex_faces(vkey, ordered=True)
        cell.add_face(cell_face, fkey=vkey)

        cell.facedata[vkey]['type'] = egi.vertex[vkey]['type']
    # cell.add_edges_from_faces()

    return cell


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _draw_arc(normal_1, normal_2, origin, layer=None, name=None):
    mid_pt = normalize_vector(add_vectors(normal_1, normal_2))
    arc    = Arc(Point3d(*[sum(axis) for axis in zip(normal_1, origin)]),
                 Point3d(*[sum(axis) for axis in zip(mid_pt, origin)]),
                 Point3d(*[sum(axis) for axis in zip(normal_2, origin)]))
    arc_as_curve = ArcCurve(arc)
    return arc_as_curve


def _reorder_pts_on_arc(pt_list, pt_key_list, arc_curve):
    # all points should be on the arc...
    dist_list = []
    sp = arc_curve.PointAtStart
    for pt in pt_list:
        dist_list.append(distance(sp, pt))
    ordered_pt_list     = [x for (y, x) in sorted(zip(dist_list, pt_list))]
    ordered_pt_key_list = [x for (y, x) in sorted(zip(dist_list, pt_key_list))]
    return ordered_pt_list, ordered_pt_key_list


def _curve_curve_intx(curve_1, curve_2):
    intersection_tolerance  = 0.01
    overlap_tolerance       = 0.0
    intersection            = CCX(curve_1,
                                  curve_2,
                                  intersection_tolerance,
                                  overlap_tolerance)
    if not intersection:
        return None
    for instance in intersection:
        return instance.PointA


def _egi_sort_v_nbrs(egi):
    """ By default, the sorting should be ccw, since the circle is typically drawn
    ccw around the local plane's z-axis...
    """
    xyz = dict((key, [attr[_] for _ in 'xyz']) for key, attr in egi.vertices(True))
    for vkey in egi.vertex:
        nbrs    = egi.vertex[vkey]['nbrs']
        plane   = Plane(Point3d(*xyz[vkey]),
                        Vector3d(*[axis for axis in egi.vertex[vkey]['normal']]))
        circle  = Circle(plane, 1)
        p_list  = []
        for nbr_vkey in nbrs:
            boolean, parameter = ArcCurve(circle).ClosestPoint(Point3d(*xyz[nbr_vkey]))
            p_list.append(parameter)
        sorted_nbrs = [key for (param, key) in sorted(zip(p_list, nbrs))]
        egi.vertex[vkey]['sorted_nbrs'] = sorted_nbrs


def _egi_find_edge_face(u, v, egi):
    """ same as duality.algorithms.find_edge_faces... using 'sorted_nbrs' instead
    """
    cycle = [u]
    while True:
        cycle.append(v)
        nbrs    = egi.vertex[v]['sorted_nbrs']
        nbr     = nbrs[nbrs.index(u) - 1]
        u, v    = v, nbr
        if v == cycle[0]:
            cycle.append(v)
            break
    return cycle


def _egi_find_faces(egi, egi_mesh):
    """ Modified, and simplified version of duality.algorithms.find_network_faces...
    since there are no leaves or open faces in a egi network.
    """
    egi_mesh.halfedge = {key: {} for key in egi.vertices()}
    for u, v in egi.edges():
        egi_mesh.halfedge[u][v] = None
        egi_mesh.halfedge[v][u] = None
    u = sorted(egi.vertices(True), key=lambda x: (x[1]['y'], x[1]['x']))[0][0]
    v = _find_first_neighbor(u, egi)

    egi_mesh.add_face(_egi_find_edge_face(u, v, egi))

    for u, v in egi.edges():


        if egi_mesh.halfedge[u][v] is None:

            egi_mesh.add_face(_egi_find_edge_face(u, v, egi))
        if egi_mesh.halfedge[v][u] is None:
            egi_mesh.add_face(_egi_find_edge_face(v, u, egi))

    return egi_mesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
