from compas.datastructures import VolMesh


def volmesh_dual_volmesh(volmesh):
    """Constructs the volmesh dual of a volmesh.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.

    Returns
    -------
    volmesh : VolMesh
        The dual volmesh object of the input volmesh.

    """

    # 1. make volmesh instance -------------------------------------------------
    dual_volmesh = VolMesh()
    dual_volmesh.attributes['name'] = 'volmesh_dual_volmesh'

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
        print("Not enough cells to create a dual volmesh.")
        return

    # 4. for each interior vertex, find neighbors ------------------------------
    for u in int_vkeys:
        cell_halffaces = []
        for v in volmesh.vertex_neighbours(u):
            edge_ckeys = volmesh.plane[u][v].values()
            ckey       = edge_ckeys[0]
            halfface   = [ckey]
            for i in range(len(edge_ckeys) - 1):
                hfkey = volmesh.cell[ckey][u][v]
                w     = volmesh.halfface_vertex_descendant(hfkey, v)
                ckey  = volmesh.plane[w][v][u]
                halfface.append(ckey)
            cell_halffaces.append(halfface)
        dual_volmesh.add_cell(cell_halffaces, ckey=u)

    return dual_volmesh


def halffaces_on_boundary(self):
    halffaces = []
    for ckey in self.cell:
        hfkeys = self.cell_halffaces(ckey)
        for hfkey in hfkeys:
            u   = self.halfface[hfkey][0]
            v   = self.halfface[hfkey][1]
            w   = self.halfface[hfkey][2]
            if self.plane[w][v][u] is None:
                halffaces.append(hfkey)
    return halffaces


def halfface_vertex_descendant(self, hfkey, key):
    if self.halfface[hfkey][-1] == key:
        return self.halfface[hfkey][0]
    i = self.halfface[hfkey].index(key)
    return self.halfface[hfkey][i + 1]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import rhinoscriptsyntax as rs

    from compas_rhino.helpers.artists.volmeshartist import VolMeshArtist
    from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

    VolMesh.halffaces_on_boundary = halffaces_on_boundary
    VolMesh.halfface_vertex_descendant = halfface_vertex_descendant

    guids   = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    volmesh = VolMesh()
    volmesh = volmesh_from_polysurfaces(volmesh, guids)
    volmesh_artist = VolMeshArtist(volmesh, layer='primal')
    volmesh_artist.draw_vertices()
    volmesh_artist.draw_edges()

    dual_volmesh = volmesh_dual_volmesh(volmesh)
    dual_volmesh_artist = VolMeshArtist(dual_volmesh, layer='dual')
    dual_volmesh_artist.draw_vertices()
    dual_volmesh_artist.draw_faces()
