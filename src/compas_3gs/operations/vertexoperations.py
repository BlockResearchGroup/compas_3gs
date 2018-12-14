from itertools import groupby

from compas.utilities.maps import geometric_key


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'vertex_merge',
    'vertex_lift'
]


def vertex_merge(volmesh, vkeys, target_xyz):

    new_vkey = volmesh._get_vertex_key(None)
    vertices = {new_vkey: target_xyz}

    cell_vkeys = {}
    for vkey in vkeys:
        for ckey in volmesh.vertex_cells(vkey):
            if ckey not in cell_vkeys:
                cell_vkeys[ckey] = []
            cell_vkeys[ckey].append(vkey)

    # construct new halffaces --------------------------------------------------
    cells = {}
    for ckey in cell_vkeys:
        cell_halffaces = {}
        vkeys = cell_vkeys[ckey]
        for hfkey in volmesh.cell_halffaces(ckey):
            halfface = [key for key in volmesh.halfface[hfkey]]
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


def vertex_lift(volmesh, vkey, hfkeys, xyz):

    x, y, z = xyz
    w       = volmesh.add_vertex(x=x, y=y, z=z)

    # check --------------------------------------------------------------------
    if not volmesh.is_vertex_boundary(vkey):
        raise ValueError('This vertex is interior.')

    # --------------------------------------------------------------------------
    for hfkey in hfkeys:
        halffaces = [volmesh.halfface_vertices(hfkey)[::-1]]
        for u, v in volmesh.halfface_halfedges(hfkey):
            halffaces.append([u, v, w])
        volmesh.add_cell(halffaces)

    return volmesh


def vertex_truncate(volmesh, vkey):
    pass


# ==============================================================================
#   helpers
# ==============================================================================


def _volmesh_cull_duplicate_edges(volmesh):
    new_edges = {vkey: {} for vkey in volmesh.vertex}
    seen      = set()
    for u, v in volmesh.edges_iter():
        edge = frozenset([u, v])
        if edge not in seen:
            new_edges[u][v] = {}
            seen.add(edge)
    volmesh.edge = new_edges
