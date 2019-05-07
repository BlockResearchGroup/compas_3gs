from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from itertools import groupby


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'vertex_lift',
    'vertex_merge',
    'vertex_truncate',
    'vertex_volumise'
]


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def vertex_lift(volmesh, vkey, target_xyz, hfkeys):
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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def vertex_merge(volmesh, vkeys, target_xyz):
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


def vertex_truncate(volmesh, vkey):
    pass


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def vertex_volumise(volmesh, vkey):
    pass


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _volmesh_cull_duplicate_edges(volmesh):
    new_edges = {vkey: {} for vkey in volmesh.vertex}
    seen      = set()
    for u, v in volmesh.edges_iter():
        edge = frozenset([u, v])
        if edge not in seen:
            new_edges[u][v] = {}
            seen.add(edge)
    volmesh.edge = new_edges
