from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'cell_subdivide_barycentric',
    'cell_collapse_short_edges'
]


def cell_subdivide_barycentric(volmesh, ckey):

    new_ckeys = []
    x, y, z   = volmesh.cell_center(ckey)
    w         = volmesh.add_vertex(x=x, y=y, z=z)

    new_cells = []
    halffaces = volmesh.cell_halffaces(ckey)

    for hfkey in halffaces:
        cell_halffaces = [volmesh.halfface_vertices(hfkey)]

        halfedges = volmesh.halfface_halfedges(hfkey)

        for u, v in halfedges:
            cell_halffaces.append([w, v, u])

        volmesh.delete_halfface(hfkey)
        new_ckeys.append(volmesh.add_cell(cell_halffaces))

    del volmesh.cell[ckey]

    return new_ckeys


def cell_collapse_short_edges(mesh, min_length=0.1):

    new_xyz = {vkey: [] for vkey in mesh.vertex}

    for u, v in mesh.edges():
        sp   = mesh.vertex_coordinates(u)
        ep   = mesh.vertex_coordinates(v)
        dist = distance_point_point(sp, ep)
        if dist < min_length:
            print('midpoint', u, v)
            mp = midpoint_point_point(sp, ep)
            new_xyz[u].append(mp)
            new_xyz[v].append(mp)

    for vkey in new_xyz:
        if new_xyz[vkey]:
            final_xyz = centroid_points(new_xyz[vkey])
            mesh.vertex_update_xyz(vkey, final_xyz)

    return mesh





# def halfface_pinch(volmesh, hfkey, xyz):
#     x, y, z = xyz
#     w       = volmesh.add_vertex(x=x, y=y, z=z)

#     cell_halffaces = [volmesh.halfface_vertices(hfkey).reverse()]

#     halfedges = volmesh.halfface_halfedges(hfkey)
#     for u, v in halfedges:
#             cell_halffaces.append([w, v, u])

# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
