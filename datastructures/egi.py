from __future__ import print_function

from compas.geometry import angle_vectors
from compas.geometry import is_ccw_xy
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import angle_vectors
from compas.geometry import translate_points
from compas.geometry import rotate_points
from compas.geometry import area_polygon
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import normal_polygon
from compas.geometry import add_vectors
from compas.geometry import scale_vector

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
            egi.add_vertex(vkey=hfkey, x=x, y=y, z=z)
            egi.update_v_data(hfkey)

        for vkey in vertices:
            face = volmesh.cell_vertex_neighbours(ckey, vkey)
            egi.add_face(face, fkey=vkey)
            egi.update_f_data(vkey)

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
