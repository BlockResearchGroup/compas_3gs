from itertools import groupby

from compas.geometry import dot_vectors

from compas.geometry import convex_hull

from compas.datastructures.mesh import Mesh


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'halfface_pinch',
    'halfface_extrude',
    'halfface_divide',
    'halfface_merge'
]


def halfface_pinch(volmesh, hfkey, xyz):
    """

    """

    x, y, z        = xyz
    w              = volmesh.add_vertex(x=x, y=y, z=z)
    hf_vkeys       = volmesh.halfface_vertices(hfkey)
    cell_halffaces = [hf_vkeys[::-1]]
    halfedges      = volmesh.halfface_halfedges(hfkey)
    for u, v in halfedges:
        cell_halffaces.append([u, v, w])
    volmesh.add_cell(cell_halffaces)
    return volmesh


def halfface_extrude(volmesh, hfkey):
    pass


def halfface_divide(volmesh, hfkey):
    pass


def halfface_merge(volmesh, hfkeys):

    # check halffaces ----------------------------------------------------------
    for hfkey in hfkeys:
        if not volmesh.is_face_boundary(hfkey):
            raise ValueError('Halfface {} is interior.'.format(hfkey))
    if not _are_halffaces_chained(volmesh, hfkeys):
        raise ValueError('These halffaces are not chained.')
    # --------------------------------------------------------------------------
    halffaces = [volmesh.halfface[hfkey] for hfkey in hfkeys]
    # --------------------------------------------------------------------------
    vkeys = set()
    for hfkey in hfkeys:
        for key in volmesh.halfface_vertices(hfkey):
            vkeys.add(key)

    vkeys  = list(vkeys)
    points = [volmesh.vertex_coordinates(vkey) for vkey in vkeys]

    faces_by_index = convex_hull(points)
    faces_by_vkeys = []
    for face in faces_by_index:
        faces_by_vkeys.append([vkeys[index] for index in face])

    # make temp cell mesh ------------------------------------------------------
    cell = Mesh()
    for i in range(len(vkeys)):
        key     = vkeys[i]
        x, y, z = points[i]
        cell.add_vertex(key=key, x=x, y=y, z=z)
    for face in faces_by_vkeys:
        cell.add_face(face)

    # merge coplanar faces -----------------------------------------------------
    _merge_planar_neighbour_faces(cell)

    # get correct direction of faces -------------------------------------------
    faces = [cell.face[fkey] for fkey in cell.face]
    if halffaces[0] in faces:
        new_faces = [face[::-1] for face in faces]
    else:
        new_faces = faces

    volmesh.add_cell(new_faces)

    return volmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _are_halffaces_chained(volmesh, hfkeys):
    chained = set()
    for hfkey_1 in hfkeys:
        nbrs = []
        for u, v in volmesh.halfface_halfedges(hfkey_1):
            nbrs += volmesh.edge_halffaces(u, v)
        for hfkey_2 in hfkeys:
            if hfkey_2 != hfkey_1 and hfkey_2 in nbrs:
                chained.add(hfkey_1)
                chained.add(hfkey_2)
    if len(hfkeys) == 1 or len(chained) == len(hfkeys):
        return True
    return False


def _merge_planar_neighbour_faces(mesh, tol=0.001):

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
