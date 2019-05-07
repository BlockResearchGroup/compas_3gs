from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_3gs.datastructures import Mesh3gs

from compas.geometry import add_vectors


__all__ = ['EGI']


class EGI(Mesh3gs):
    """An EGI, represented as a mesh object.

    An EGI is a topological (mesh) dual of a cell of a volmesh, with all of its elements represented on a unit sphere.

    """

    def __init__(self):
        super(EGI, self).__init__()

        a  = {'origin': (0, 0, 0)}
        va = {'x_fix' : False,
              'y_fix' : False,
              'z_fix' : False,
              'type'  : None,
              'normal': None,
              'target_area': None}
        ea = {}
        fa = {}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)
        self.default_face_attributes.update(fa)

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
            normal  = volmesh.halfface_oriented_normal(hfkey)
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
    from compas_rhino.artists import VolMeshArtist
    from compas_3gs.datastructures.forcevolmesh import ForceVolMesh as VolMesh
    from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

    guids   = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    volmesh = VolMesh()
    volmesh = volmesh_from_polysurfaces(volmesh, guids)
    volmesh_artist = VolMeshArtist(volmesh, layer='primal')
    volmesh_artist.draw_vertices()
    volmesh_artist.draw_edges()

    for ckey in volmesh.cell:
        egi = EGI.from_volmesh_cell(ckey, volmesh)
        egi.draw()
