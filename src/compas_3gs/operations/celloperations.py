from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.datastructures import VolMesh

from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point


__all__ = [
    'cell_face_split_vertices',
    'cell_split_vertex',
    'cell_subdivide_barycentric',
    'cell_collapse_short_edges'
]


def cell_face_split_vertices(self, hfkey):
    hf_vkeys = self.halfface_vertices(hfkey)


def cell_split_vertex(self, vkey, hfkey1, hfkey2):

    if len(self.cell) > 1:
        raise ValueError('This is a multi-cell volmesh.')

    ckey = self.cell.keys()[0]
    halffaces = self.cell_vertex_halffaces(ckey, vkey)
    i = halffaces.index(hfkey1)
    j = halffaces.index(hfkey2)

    if i + 1 == j or j + 1 == i:
        raise ValueError('The two halffaces are adjacent.')

    egi = self.c_data[ckey]['egi']
    hfkeys = egi.face_vertices(vkey)

    f, g = egi.mesh_split_face(vkey, hfkey1, hfkey2)

    x, y, z = self.vertex_coordinates(vkey)
    self.add_vertex(key=f, x=x, y=y, z=z)
    self.add_vertex(key=g, x=x, y=y, z=z)

    # new halffaces ------------------------------------------------------------
    for hfkey in hfkeys:
        new_vkeys = egi.vertex_faces(hfkey, ordered=True)
        self.add_halfface(new_vkeys[::-1], fkey=hfkey)

    print('f', f)
    print('g', g)
    print('hfkey1', self.halfface[hfkey1])
    print('hfkey2', self.halfface[hfkey2])

    self.cell_vertex_delete(vkey)

    print(egi.face)


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

    # new_xyz = {vkey: [] for vkey in mesh.vertex}

    # for u, v in mesh.edges():
    #     sp   = mesh.vertex_coordinates(u)
    #     ep   = mesh.vertex_coordinates(v)
    #     dist = distance_point_point(sp, ep)
    #     if dist < min_length:
    #         print('midpoint', u, v)
    #         mp = midpoint_point_point(sp, ep)
    #         new_xyz[u].append(mp)
    #         new_xyz[v].append(mp)

    # for vkey in new_xyz:
    #     if new_xyz[vkey]:
    #         final_xyz = centroid_points(new_xyz[vkey])
    #         mesh.vertex_update_xyz(vkey, final_xyz)


    for u, v in mesh.edges():
        sp   = mesh.vertex_coordinates(u)
        ep   = mesh.vertex_coordinates(v)
        dist = distance_point_point(sp, ep)
        if dist < min_length:
            mp = midpoint_point_point(sp, ep)
            mesh.vertex_update_xyz(u, mp)
            mesh.vertex_update_xyz(v, mp)

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
