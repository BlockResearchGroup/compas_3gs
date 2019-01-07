from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from copy import deepcopy

from compas.datastructures import Mesh

from compas.datastructures.mesh.operations import mesh_split_face

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import cross_vectors

from compas_rhino.artists import MeshArtist

from compas_rhino.helpers.mesh import mesh_draw
from compas_rhino.helpers.mesh import mesh_draw_vertices
from compas_rhino.helpers.mesh import mesh_draw_edges

from compas_3gs.utilities import normal_polygon_general
from compas_3gs.utilities import area_polygon_general
from compas_3gs.utilities import datastructure_centroid


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'Mesh3gs'
]


class Mesh3gs(Mesh):
    """Inherits and extends the Mesh class, such that it is more suitable for 3DGS purposes.

    Primarily used for the EGI.

    """

    def __init__(self):
        super(Mesh3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   inherited
    # --------------------------------------------------------------------------

    mesh_split_face        = mesh_split_face
    datastructure_centroid = datastructure_centroid

    # --------------------------------------------------------------------------
    #   updaters / setters
    # --------------------------------------------------------------------------

    # def update_v_data(self, vkey, attr_dict=None, **kwattr):
    #     if vkey not in self.v_data:
    #         self.v_data[vkey] = {}
    #     attr = self.default_v_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.v_data[vkey].update(attr)

    # def update_e_data(self, u, v, attr_dict=None, **kwattr):
    #     if (u, v) not in self.e_data:
    #         self.e_data[u, v] = {}
    #     attr = self.default_e_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.e_data[u, v].update(attr)

    # def update_f_data(self, fkey, attr_dict=None, **kwattr):
    #     if fkey not in self.f_data:
    #         self.f_data[fkey] = {}
    #     attr = self.default_f_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.f_data[fkey].update(attr)

    # def initalize_data(self):
    #     for vkey in self.vertex:
    #         self.update_v_data(vkey)
    #     for u, v in self.edges():
    #         self.update_e_data(u, v)
    #     for fkey in self.halfface:
    #         self.update_f_data(fkey)

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
        vertices = self.face[fkey]
        points   = [self.vertex_coordinates(vkey) for vkey in vertices]
        area     = area_polygon_general(points)
        return area

    def face_normal(self, fkey, unitized=True):
        vertices = self.face[fkey]
        points   = [self.vertex_coordinates(vkey) for vkey in vertices]
        normal   = normal_polygon_general(points, unitized)
        if length_vector(normal) == 0 :
            uv = subtract_vectors(points[1], points[0])
            vw = subtract_vectors(points[2], points[1])
            normal = normalize_vector(cross_vectors(uv, vw))
        return normal

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        mesh_draw(self, clear_vertices=True, clear_faces=True, clear_edges=True, **kwattr)

    def draw_vertices(self, **kwattr):
        mesh_draw_vertices(self, **kwattr)

    def draw_edges(self, **kwattr):
        mesh_draw_edges(self, **kwattr)

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
