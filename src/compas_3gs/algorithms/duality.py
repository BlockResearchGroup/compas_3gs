from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_3gs.datastructures import Network3gs as Network
from compas_3gs.datastructures import VolMesh3gs as VolMesh


__all__ = ['volmesh_dual_volmesh',
           'volmesh_dual_network']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh  >>>  dual volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_dual_volmesh(volmesh, cls=None):
    """Constructs the dual volmesh of a volmesh.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.

    Returns
    -------
    volmesh : VolMesh
        The dual volmesh object of the input volmesh.

    """

    if not cls:
        cls = VolMesh

    # 1. make volmesh instance -------------------------------------------------
    dual_volmesh = cls()
    dual_volmesh.attributes['name'] = 'volmesh_dual_volmesh'

    # 2. add vertex for each cell ----------------------------------------------
    for cell in volmesh.cells():
        x, y, z = volmesh.cell_centroid(cell)
        dual_volmesh.add_vertex(vkey=cell, x=x, y=y, z=z)

    # 3. find interior vertices ------------------------------------------------
    ext_vkeys = []
    boundary_hfkeys = volmesh.halffaces_on_boundaries()
    for halfface in boundary_hfkeys:
        for vertex in volmesh.halfface_vertices(halfface):
            ext_vkeys.append(vertex)
    int_vkeys = list(set(volmesh.vertices()) - set(ext_vkeys))

    if len(int_vkeys) < 1:
        raise Exception('Not enough cells to create a dual volmesh.')

    # 4. for each interior vertex, find neighbors ------------------------------
    for u in int_vkeys:
        cell_halffaces = []
        for v in volmesh.vertex_neighbors(u):
            halfface = volmesh.edge_cells((u, v))
            # edge_ckeys = volmesh.plane[u][v].values()
            # ckey       = edge_ckeys[0]
            # halfface   = [ckey]
            # for i in range(len(edge_ckeys) - 1):
            #     hfkey = volmesh.cell[ckey][u][v]
            #     w     = volmesh.halfface_vertex_descendent(hfkey, v)
            #     ckey  = volmesh.plane[w][v][u]
            #     halfface.append(ckey)
            cell_halffaces.append(halfface)

        dual_volmesh.add_cell(cell_halffaces, ckey=u)

    return dual_volmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh  >>>  dual network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_dual_network(volmesh, cls=None):
    """Computes the dual network dual of a volmesh.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.

    Returns
    -------
    network : Network
        The dual network object of the input volmesh.

    """
    if not cls:
        cls = Network

    dual_network = cls()

    for cell in volmesh.cells():
        x, y, z = volmesh.cell_centroid(cell)
        dual_network.add_node(key=cell, x=x, y=y, z=z)

        for nbr in volmesh.cell_neighbors(cell):
            if nbr in dual_network.edge[cell]:
                continue
            if nbr in dual_network.edge and cell in dual_network.edge[nbr]:
                continue
            dual_network.add_edge(cell, nbr)

    return dual_network


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
