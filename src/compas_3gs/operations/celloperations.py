from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import dot_vectors
from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point


__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['cell_collapse_short_edges',

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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell edges
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_collapse_short_edges(cell, min_length=0.1):
    """Collapse short edges of a cell.

    Parameters
    ----------
    cell : mesh
        Cell as a mesh object.
    min_length : float
        Minimum length of edges to be collapsed.

    Returns
    -------
    cell : mesh
        Updated cell.

    """
    for u, v in cell.edges():
        sp   = cell.vertex_coordinates(u)
        ep   = cell.vertex_coordinates(v)
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


def cell_face_subdivide_barycentric(mesh, fkey):
    raise NotImplementedError


def cell_merge_coplanar_adjacent_faces(mesh, tol=0.001):

    initial_faces = [key for key in mesh.face]
    current_faces = [key for key in mesh.face]

    for fkey in initial_faces:

        if fkey in current_faces:
            normal = mesh.face_normal(fkey)

            faces_to_delete = []

            for nbr_fkey in mesh.face_neighbours(fkey):
                nbr_normal = mesh.face_normal(nbr_fkey)
                dot = dot_vectors(normal, nbr_normal)
                if 1 - dot < tol:
                    faces_to_delete.append(nbr_fkey)

            if faces_to_delete:
                new_halfedges = mesh.face_halfedges(fkey)
                for del_fkey in faces_to_delete:
                    for u, v in mesh.face_halfedges(del_fkey):
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
                    mesh.delete_face(key)
                    current_faces.remove(key)

                mesh.add_face(vertices=new_face, fkey=fkey)

    return mesh


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
