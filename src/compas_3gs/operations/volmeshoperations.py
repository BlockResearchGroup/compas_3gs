from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector

from itertools import groupby

from compas.datastructures import Mesh

from compas.geometry import convex_hull

from compas_3gs.utilities import datastructure_centroid

from compas_3gs.operations import cell_merge_coplanar_adjacent_faces

__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['point_reflection',

           'volmesh_vertex_lift',
           'volmesh_vertex_merge',

           'volmesh_halfface_pinch',
           'volmesh_halfface_extrude',
           'volmesh_halfface_subdivide',
           'volmesh_merge_adjacent_halffaces',

           'volmesh_cell_split_vertex',
           'volmesh_cell_subdivide_barycentric']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh global operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def point_reflection(datastructure):
    """Inverts a datastructure through its centroid.

    Parameters
    ----------
    datastructure
        A network, mesh or volmesh object.

    Returns
    -------
        The datastructure with new vertex coordinates.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Point_reflection

    """
    center = datastructure_centroid(datastructure)

    for vkey in datastructure.vertex:
        xyz     = datastructure.vertex_coordinates(vkey)
        vector  = scale_vector(subtract_vectors(center, xyz), 2)
        new_xyz = add_vectors(xyz, vector)
        datastructure.vertex_update_xyz(vkey, new_xyz, constrained=False)


def reverse_cycle_directions(volmesh):
    raise NotImplementedError


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh vertex operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_vertex_lift(volmesh, vkey, target_xyz, hfkeys):
    """Duplicates and lifts a vertex, then creates cells using the vertex halffaces and the duplicated vertex.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object representing a polyhedral force diagram.
    vkey : int
        The key of the vertex to lift.
    hfkeys : list
        List of halfface keys to create new cells from.
    xyz : tuple
        Target xyz coordinates of the lifted vertex.

    Notes
    -----
    The lifting vertex must be on the boundary of the volmesh.

    See Also
    --------
    * :func:`compas_3gs.operations.face_pinch`

    """

    # check if vertex is interior ----------------------------------------------
    if not volmesh.is_vertex_on_boundary(vkey):
        raise Exception('This vertex is interior.')

    # add new, lifted vertex ---------------------------------------------------
    x, y, z = target_xyz
    w       = volmesh.add_vertex(x=x, y=y, z=z)

    # add cells ----------------------------------------------------------------
    for hfkey in hfkeys:
        halffaces = [volmesh.halfface_vertices(hfkey)[::-1]]
        for u, v in volmesh.halfface_halfedges(hfkey):
            halffaces.append([u, v, w])
        volmesh.add_cell(halffaces)

    # --------------------------------------------------------------------------
    return volmesh


def volmesh_vertex_merge(volmesh, vkeys, target_xyz):
    """Merges specified vertices to a single vertex.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object representing a polyhedral force diagram.
    vkeys : list
        List of vertices to merge.
    target_xyz : tuple
        Target xyz coordinates of the vertices to be merged.

    Notes
    -----
    As implemented, the merging vertices (in any combination) must be a continuous chain of halfedges of a halfface.
    For example, vertices 1 and 3 cannot be merged.

    0 ------ 1
    |        |
    |        |
    |        |
    3 ------ 2

    """

    # inspect vertices ---------------------------------------------------------
    hf_vkeys = {}
    for vkey in vkeys:
        for hfkey in volmesh.vertex_halffaces(vkey):
            if hfkey not in hf_vkeys:
                hf_vkeys[hfkey] = []
            hf_vkeys[hfkey].append(vkey)

    for hfkey in hf_vkeys:
        all_vkeys = volmesh.halfface[hfkey]
        test_vkeys = set(hf_vkeys[hfkey])

        if len(test_vkeys) == 1:
            continue

        if len(all_vkeys) - len(test_vkeys) <= 1:
            raise Exception("Illegal merge!")

        for vkey in test_vkeys:
            anc = volmesh.halfface_vertex_ancestor(hfkey, vkey)
            des = volmesh.halfface_vertex_descendent(hfkey, vkey)
            if anc not in test_vkeys and des not in test_vkeys:
                raise Exception("Illegal merge!")

    # get vertex cells ---------------------------------------------------------
    new_vkey = volmesh._get_vertex_key(None)
    vertices = {new_vkey: target_xyz}

    cell_vkeys = {}
    for vkey in vkeys:
        for ckey in volmesh.vertex_cells(vkey):
            if ckey not in cell_vkeys:
                cell_vkeys[ckey] = []
            cell_vkeys[ckey].append(vkey)

    # construct new cell halffaces ---------------------------------------------
    cells = {}
    for ckey in cell_vkeys:
        cell_halffaces = {}
        vkeys = cell_vkeys[ckey]

        for hfkey in volmesh.cell_halffaces(ckey):
            halfface = [vkey for vkey in volmesh.halfface[hfkey]]
            for index, item in enumerate(halfface):
                if item in vkeys:
                    halfface[index] = new_vkey
            halfface = [key[0] for key in groupby(halfface)]
            if len(set(halfface)) > 2:
                cell_halffaces[hfkey] = halfface
        cells[ckey] = cell_halffaces
        for c_vkey in volmesh.cell_vertices(ckey):
            vertex_ckeys = volmesh.vertex_cells(c_vkey)
            if len(vertex_ckeys) == 1:
                if c_vkey not in vkeys:
                    vertices[c_vkey] = volmesh.vertex_coordinates(c_vkey)
        volmesh.delete_cell(ckey)

    # add vertices -------------------------------------------------------------
    for vkey in vertices:
        x, y, z = vertices[vkey]
        volmesh.add_vertex(vkey=vkey, x=x, y=y, z=z)

    # add halffaces and cells --------------------------------------------------
    for ckey in cells:
        volmesh.cell[ckey] = {}
        for hfkey in cells[ckey]:
            vertices = cells[ckey][hfkey]
            volmesh.add_halfface(vertices, fkey=hfkey)
            vertices = volmesh.halfface[hfkey]
            for i in range(-2, len(vertices) - 2):
                u = vertices[i]
                v = vertices[i + 1]
                w = vertices[i + 2]
                if u not in volmesh.cell[ckey]:
                    volmesh.cell[ckey][u] = {}
                volmesh.cell[ckey][u][v] = hfkey
                volmesh.plane[u][v][w] = ckey

    # --------------------------------------------------------------------------
    return volmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh edge operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def _volmesh_cull_duplicate_edges(volmesh):
#     new_edges = {vkey: {} for vkey in volmesh.vertex}
#     seen      = set()
#     for u, v in volmesh.edges():
#         edge = frozenset([u, v])
#         if edge not in seen:
#             new_edges[u][v] = {}
#             seen.add(edge)
#     volmesh.edge = new_edges


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh halfface operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_halfface_extrude(volmesh, hfkey):
    raise NotImplementedError


def volmesh_halfface_subdivide(volmesh, hfkey):
    raise NotImplementedError


def volmesh_halfface_pinch(volmesh, hfkey, xyz):
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


def volmesh_merge_adjacent_halffaces(volmesh, hfkeys):

    # check halffaces ----------------------------------------------------------
    for hfkey in hfkeys:
        if not volmesh.is_halfface_on_boundary(hfkey):
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
    cell_merge_coplanar_adjacent_faces(cell)

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
#   volmesh cell operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_cell_split_vertex(self, vkey, hfkey1, hfkey2):

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

    self.cell_vertex_delete(vkey)

    print(egi.face)


def volmesh_cell_subdivide_barycentric(volmesh, ckey):
    """Subdivide a cell of a volmesh.

    """
    new_ckeys = []
    x, y, z   = volmesh.cell_center(ckey)
    w         = volmesh.add_vertex(x=x, y=y, z=z)

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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh operation helpers
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
