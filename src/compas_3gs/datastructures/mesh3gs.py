from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from copy import deepcopy

from compas.datastructures import Mesh

from compas.datastructures.mesh import mesh_split_face

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import cross_vectors

from compas_rhino.artists import MeshArtist

from compas_rhino.utilities import draw_mesh

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented
from compas_3gs.utilities import datastructure_centroid


__all__ = ['Mesh3gs']


class Mesh3gs(Mesh):
    """Inherits and extends the compas Mesh class, such that it is more suitable for 3D graphic statics applications.

    Primarily used for the EGI.

    """

    def __init__(self):
        super(Mesh3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   inherited
    # --------------------------------------------------------------------------

    mesh_split_face = mesh_split_face
    datastructure_centroid = datastructure_centroid

    def add_edge(self, u, v, attr_dict=None, **kwattr):

        attr = deepcopy(self.default_edge_attributes)
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)

        if u not in self.vertex:
            u = self.add_vertex(u)
        if v not in self.vertex:
            v = self.add_vertex(v)

        data = self.edge[u].get(v, {})
        data.update(attr)

        self.edge[u][v] = data
        if v not in self.halfedge[u]:
            self.halfedge[u][v] = None
        if u not in self.halfedge[v]:
            self.halfedge[v][u] = None

        return u, v

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, vkey, xyz, constrained=True):
        if constrained:
            # X
            if self.vertex[vkey]['x_fix'] is False:
                self.vertex[vkey]['x'] = xyz[0]
            # Y
            if self.vertex[vkey]['y_fix'] is False:
                self.vertex[vkey]['y'] = xyz[1]
            # Z
            if self.vertex[vkey]['z_fix'] is False:
                self.vertex[vkey]['z'] = xyz[2]
        else:
            self.vertex[vkey]['x'] = xyz[0]
            self.vertex[vkey]['y'] = xyz[1]
            self.vertex[vkey]['z'] = xyz[2]

    # --------------------------------------------------------------------------
    # helpers - faces
    # --------------------------------------------------------------------------

    def face_area(self, fkey):
        points = self.face_coordinates(fkey)
        area = polygon_area_oriented(points)
        return area

    def face_normal(self, fkey, unitized=True):
        points = self.face_coordinates(fkey)
        normal = polygon_normal_oriented(points, unitized)
        if length_vector(normal) == 0:
            uv = subtract_vectors(points[1], points[0])
            vw = subtract_vectors(points[2], points[1])
            normal = normalize_vector(cross_vectors(uv, vw))
        return normal

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        draw_mesh(self, clear_vertices=True, clear_faces=True, clear_edges=True, **kwattr)

    def clear(self, **kwattr):
        artist = MeshArtist(self)
        artist.clear_by_name()

    def draw_vertices(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_vertices(**kwattr)

    def draw_edges(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_edges(**kwattr)

    def draw_faces(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_faces(**kwattr)

    def draw_vertexlabels(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_vertexlabels(**kwattr)

    def draw_edgelabels(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_edgelabels(**kwattr)

    def draw_facelabels(self, **kwattr):
        artist = MeshArtist(self)
        artist.draw_facelabels(**kwattr)


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
