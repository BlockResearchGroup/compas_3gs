from compas.geometry import add_vectors

from compas.datastructures import Mesh


class EGI(Mesh):
    """Definition of an egi.

    An EGI is a topological mesh dual of a cell of a volmesh, with all of its vertices represented on a unit sphere.

    """

    def __init__(self):
        super(EGI, self).__init__()

    # --------------------------------------------------------------------------
    #   constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_volmesh_cell(cls, ckey, volmesh):
        egi    = cls()
        origin = volmesh.cell_centroid(ckey)
        egi.attributes['name']   = ckey
        egi.attributes['origin'] = origin

        halffaces = volmesh.cell_halffaces(ckey)
        vertices  = volmesh.cell_vertices(ckey)

        for hfkey in halffaces:
            normal  = volmesh.halfface_normal(hfkey)
            x, y, z = add_vectors(origin, normal)
            egi.add_vertex(key=hfkey, x=x, y=y, z=z)

        for vkey in vertices:
            face = volmesh.cell_vertex_halffaces(ckey, vkey)
            egi.add_face(face, fkey=vkey)

        return egi


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import rhinoscriptsyntax as rs

    from compas.datastructures import VolMesh

    from compas.geometry import normal_polygon
    from compas.geometry import center_of_mass_polygon

    from compas_rhino.helpers.artists.volmeshartist import VolMeshArtist
    from compas_rhino.helpers.artists.meshartist import MeshArtist
    from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

    # --------------------------------------------------------------------------
    # volmesh function to be added to VolMesh class in the future...
    # --------------------------------------------------------------------------

    def face_center(self, fkey):
        return center_of_mass_polygon(self.halfface_coordinates(fkey))

    def halfface_coordinates(self, hfkey):
        return [self.vertex_coordinates(key) for key in self.halfface_vertices(hfkey)]

    def halfface_vertex_ancestor(self, hfkey, key):
        i = self.halfface[hfkey].index(key)
        return self.halfface[hfkey][i - 1]

    def halfface_normal(self, hfkey):
        return normal_polygon(self.halfface_coordinates(hfkey))

    def cell_vertex_halffaces(self, ckey, vkey):
        nbr_vkeys = self.cell[ckey][vkey].keys()
        u = vkey
        v = nbr_vkeys[0]
        ordered_hfkeys = []
        for i in range(len(nbr_vkeys)):
            hfkey = self.cell[ckey][u][v]
            v     = self.halfface_vertex_ancestor(hfkey, u)
            ordered_hfkeys.append(hfkey)
        return ordered_hfkeys

    VolMesh.face_center              = face_center
    VolMesh.halfface_normal          = halfface_normal
    VolMesh.halfface_coordinates     = halfface_coordinates
    VolMesh.halfface_vertex_ancestor = halfface_vertex_ancestor
    VolMesh.cell_vertex_halffaces    = cell_vertex_halffaces

    # --------------------------------------------------------------------------
    # for testing in Rhino: pick any single or multiple, connected cells
    # --------------------------------------------------------------------------

    guids   = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    volmesh = VolMesh()
    volmesh = volmesh_from_polysurfaces(volmesh, guids)
    volmesh_artist = VolMeshArtist(volmesh, layer='volmesh')
    volmesh_artist.draw_vertexlabels(color=(0, 0, 0))
    volmesh_artist.draw_edges()
    volmesh_artist.draw_facelabels(color=(255, 0, 0))

    for ckey in volmesh.cell:
        egi = EGI()
        egi = egi.from_volmesh_cell(ckey, volmesh)
        egi_artist = MeshArtist(egi, layer='egi')
        egi_artist.draw_vertexlabels(color=(255, 150, 150))
        egi_artist.draw_faces()
        egi_artist.draw_facelabels(color=(150, 150, 150))
