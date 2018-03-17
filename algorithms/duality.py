from compas_3gs.datastructures._3gs_volmesh import _3gs_VolMesh as VolMesh


def volmesh_dual(volmesh):

    # 1. make volmesh instance -------------------------------------------------
    dual_volmesh = VolMesh()
    dual_volmesh.attributes['name'] = 'dual_volmesh'

    # 2. add vertex for each cell ----------------------------------------------
    for ckey in volmesh.cell:
        x, y, z = volmesh.cell_centroid(ckey)
        dual_volmesh.add_vertex(vkey=ckey, x=x, y=y, z=z)

    # 3. find interior vertices ------------------------------------------------
    ext_vkeys = []
    boundary_hfkeys = volmesh.halffaces_on_boundary()
    for hfkey in boundary_hfkeys:
        for vkey in volmesh.halfface[hfkey]:
            ext_vkeys.append(vkey)
    int_vkeys = list(set(volmesh.vertices()) - set(ext_vkeys))

    if len(int_vkeys) < 1:
        print("Not enough cells to create a dual volmesh!")
        return

    # 4. for each interior vertex, find neighbors ------------------------------
    for vkey in int_vkeys:
        cell_halffaces = []
        # 5. for each vkey --> nbr_vkey, make a halfface -----------------------
        for nbr_vkey in volmesh.vertex_neighbours(vkey):
            ordered_ckeys = []
            u = vkey
            v = nbr_vkey
            ordered_ckeys = _sort_edge_cells(volmesh, u, v)
            cell_halffaces.append(ordered_ckeys)
            print(vkey, ordered_ckeys)
        dual_volmesh.add_cell(cell_halffaces, ckey=vkey)

    return dual_volmesh


def _sort_edge_cells(volmesh, u, v):
    nbr_ckeys = volmesh.edge_cells(u, v)
    if len(nbr_ckeys) < 3:
        return nbr_ckeys

    halfedges = {}
    for ckey in nbr_ckeys:
        hfkey = volmesh.cell[ckey][u][v]
        w = volmesh.halfface[hfkey][v]
        next_ckey = volmesh.plane[w][v][u]
        halfedges[ckey] = next_ckey

    ordered_ckeys = []

    ckey = halfedges.keys()[0]
    ordered_ckeys.append(ckey)
    while len(ordered_ckeys) != len(halfedges):
        ordered_ckeys.append(halfedges[ckey])
        ckey = halfedges[ckey]

    return ordered_ckeys
