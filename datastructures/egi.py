from __future__ import print_function

from compas.geometry import angle_vectors


from compas_3gs.datastructures.mesh3gs import Mesh3gs as Mesh


class EGI(Mesh):
    """Definition of an egi.

    An EGI is a topological (mesh) dual of a cell of a volmesh, with all of its elements represented on a unit sphere.

    """

    def __init__(self):
        super(EGI, self).__init__()

        self.v_data = {}
        self.e_data = {}
        self.f_data = {}

        self.default_v_prop = {
            'x_fix' : False,
            'y_fix' : False,
            'z_fix' : False,
            'weight': None}

        self.default_e_prop = {}

        self.default_f_prop = {}

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

    # from compas.datastructures import VolMesh
    from compas_rhino.helpers.artists.volmeshartist import VolMeshArtist
    from compas_3gs.datastructures.forcevolmesh import ForceVolMesh as VolMesh
    from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

    guids   = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    volmesh = VolMesh()
    volmesh = volmesh_from_polysurfaces(volmesh, guids)
    volmesh_artist = VolMeshArtist(volmesh, layer='primal')
    volmesh_artist.draw_vertices()
    volmesh_artist.draw_edges()

    for ckey in volmesh:
        egi = EGI.from_volmesh_cell(ckey, volmesh)
        egi.draw()
