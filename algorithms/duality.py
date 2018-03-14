from compas_3gs.datastructures._3gs_volmesh import _3gs_VolMesh as VolMesh


def volmesh_dual(volmesh):
    """Algorithm for constructing the dual VolMesh of a VolMesh.

    volmesh --> dual_volmesh

    """

    dual_volmesh = VolMesh()

    for ckey in volmesh.cell:
        x, y, z = volmesh.cell_centroid(ckey)
        dual_volmesh.add_vertex(vkey=ckey, x=x, y=y, z=z)

    # --------------------------------------------------------------------------
    #   find interior vertices
    # --------------------------------------------------------------------------
    ext_vkeys = []
    boundary_hfkeys = volmesh.halffaces_on_boundary()
    for hfkey in boundary_hfkeys:
        for vkey in volmesh.halfface[hfkey]:
            ext_vkeys.append(vkey)
    int_vkeys = list(set(volmesh.vertices()) - set(ext_vkeys))

    if len(int_vkeys) < 1:
        print("Not enough cells to create a dual volmesh!")
        return

    # --------------------------------------------------------------------------
    #   find vertex neighbours
    # --------------------------------------------------------------------------
    for vkey in int_vkeys:
        halffaces = []
        for nbr_vkey in volmesh.vertex_neighbours(vkey):
            halffaces.append(volmesh.edge_cells(vkey, nbr_vkey))
        dual_volmesh.add_cell(halffaces, ckey=vkey)

    return dual_volmesh

