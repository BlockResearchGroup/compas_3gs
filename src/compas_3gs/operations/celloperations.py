from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import mesh_dual

from compas.geometry import dot_vectors
from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point
from compas.geometry import intersection_line_plane

from compas_3gs.diagrams import EGI


__all__ = ['cell_split_indet_face_vertices',
           'cell_collapse_short_edge',

           'cell_relocate_face',
           'cell_face_subdivide_barycentric',
           'cell_merge_coplanar_adjacent_faces']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell vertices
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_split_indet_face_vertices(cell, fkey):
    """Split all indeterminate vertices of a cell face.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    fkey : hashable
        Identifier of the face.

    Returns
    -------
    Cell
        Updated cell.

    Notes
    -----
    An indeterminate vertex is defined as a vertex with degree or valency of 3 or greater.

    """
    egi = mesh_dual(cell, EGI)

    f_vkeys = cell.face_vertices(fkey)
    egi_nbr_vkeys = egi.vertex_neighbors(fkey)

    for egi_fkey in f_vkeys:

        fkeys = egi.face_vertices(egi_fkey)
        i = fkeys.index(fkey)
        fkeys = fkeys[i:] + fkeys[:i]

        egi_face_vertices = [key for key in fkeys if key not in egi_nbr_vkeys + [fkey]]

        vkey_del = egi_fkey
        x, y, z = cell.vertex_coordinates(vkey_del)

        for vkey in egi_face_vertices:

            f, g = egi.mesh_split_face(vkey_del, fkey, vkey)

            cell.delete_vertex(vkey_del)

            cell.add_vertex(key=f, x=x, y=y, z=z)
            cell.add_vertex(key=g, x=x, y=y, z=z)

            for new_fkey in fkeys:
                new_vkeys = egi.vertex_faces(new_fkey, ordered=True)
                cell.add_face(new_vkeys, fkey=new_fkey)
            vkey_del = g

    return cell


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell edges
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_collapse_short_edge(cell, u, v, min_length=0.1):
    """Collapse short edges of a cell.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    u : hashable
        The key of the start vertex.
    v : hashable
        The key of the end vertex.
    min_length : float
        Minimum length of edges to be collapsed.

    Returns
    -------
    cell : Mesh
        Updated cell.

    """
    sp = cell.vertex_coordinates(u)
    ep = cell.vertex_coordinates(v)
    dist = distance_point_point(sp, ep)

    if dist < min_length:
        mp = midpoint_point_point(sp, ep)
        cell.vertex_update_xyz(u, mp)
        cell.vertex_update_xyz(v, mp)

    return cell


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell face operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_cull_zero_faces(cell):
    pass


def cell_relocate_face(cell, fkey, xyz, normal):
    """Relocate the face of a mesh.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    fkey : hashable
        Identifier of the face.
    xyz : tuple
        xyz coordinates of the new target plane.
    normal : tuple
        Target normal vector.

    Returns
    -------
    cell : Mesh
        Updated cell.
    """

    cell_split_indet_face_vertices(cell, fkey)

    vkeys = cell.face_vertices(fkey)

    # new target plane for the face
    plane = (xyz, normal)

    # neighboring edges
    edges = {}
    for u in vkeys:
        for v in cell.vertex_neighbors(u):
            if v not in vkeys:
                edges[u] = v

    for u in edges:
        line = cell.edge_coordinates(u, edges[u])
        it = intersection_line_plane(line, plane)
        cell.vertex_update_xyz(u, it, constrained=False)

    return cell


def cell_merge_coplanar_adjacent_faces(cell, tol=0.001):

    initial_faces = [key for key in cell.face]
    current_faces = [key for key in cell.face]

    for fkey in initial_faces:

        if fkey in current_faces:
            normal = cell.face_normal(fkey)

            faces_to_delete = []

            for nbr_fkey in cell.face_neighbours(fkey):
                nbr_normal = cell.face_normal(nbr_fkey)
                dot = dot_vectors(normal, nbr_normal)
                if 1 - dot < tol:
                    faces_to_delete.append(nbr_fkey)

            if faces_to_delete:
                new_halfedges = cell.face_halfedges(fkey)
                for del_fkey in faces_to_delete:
                    for u, v in cell.face_halfedges(del_fkey):
                        if (v, u) in new_halfedges:
                            new_halfedges.remove((v, u))
                        else:
                            new_halfedges.append((u, v))

                new_face = list(new_halfedges[0])

                for i in range(1, len(new_halfedges)):
                    u, v = new_halfedges[i]
                    if u in new_face:
                        index = new_face.index(u)
                        new_face.insert(index + 1, v)
                    else:
                        index = new_face.index(v)
                        new_face.insert(index, u)

                for key in faces_to_delete:
                    cell.delete_face(key)
                    current_faces.remove(key)

                cell.add_face(vertices=new_face, fkey=fkey)

    return cell


def cell_face_subdivide_barycentric(cell, fkey):
    raise NotImplementedError


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
