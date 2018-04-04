from __future__ import print_function

from compas.datastructures import Mesh

from compas_rhino.helpers.artists.meshartist import MeshArtist

from compas_rhino.helpers.mesh import mesh_draw
from compas_rhino.helpers.mesh import mesh_draw_vertices
from compas_rhino.helpers.mesh import mesh_draw_edges
from compas_rhino.helpers.mesh import mesh_draw_faces

from compas_rhino.helpers.mesh import mesh_draw_vertex_labels
from compas_rhino.helpers.mesh import mesh_draw_edge_labels
from compas_rhino.helpers.mesh import mesh_draw_face_labels

from compas_rhino.helpers.mesh import mesh_select_vertices
from compas_rhino.helpers.mesh import mesh_select_vertex
from compas_rhino.helpers.mesh import mesh_select_edges
from compas_rhino.helpers.mesh import mesh_select_edge
from compas_rhino.helpers.mesh import mesh_select_faces
from compas_rhino.helpers.mesh import mesh_select_face


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


class Mesh3gs(Mesh):
    """Inherits and extends the Mesh class, such that it is more suitable for 3DGS purposes.

    Primarily used for the EGI.

    """

    def __init__(self):
        super(Mesh3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   updaters / setters
    # --------------------------------------------------------------------------

    def update_v_data(self, vkey, attr_dict=None, **kwattr):
        if vkey not in self.v_data:
            self.v_data[vkey] = {}
        attr = self.default_v_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.v_data[vkey].update(attr)

    def update_e_data(self, u, v, attr_dict=None, **kwattr):
        if (u, v) not in self.e_data:
            self.e_data[u, v] = {}
        attr = self.default_e_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.e_data[u, v].update(attr)

    def update_f_data(self, fkey, attr_dict=None, **kwattr):
        if fkey not in self.f_data:
            self.f_data[fkey] = {}
        attr = self.default_f_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.f_data[fkey].update(attr)

    def initalize_data(self):
        for vkey in self.vertex:
            self.update_v_data(vkey)
        for u, v in self.edges():
            self.update_e_data(u, v)
        for fkey in self.halfface:
            self.update_f_data(fkey)

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, vkey, xyz):
        # X
        if self.v_data[vkey]['x_fix'] is False:
            self.vertex[vkey]['x'] = xyz[0]
        # Y
        if self.v_data[vkey]['y_fix'] is False:
            self.vertex[vkey]['y'] = xyz[1]
        # Z
        if self.v_data[vkey]['z_fix'] is False:
            self.vertex[vkey]['z'] = xyz[2]

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        mesh_draw(self, **kwattr)

    def draw_vertices(self, **kwattr):
        mesh_draw_vertices(self, **kwattr)

    def draw_edges(self, **kwattr):
        mesh_draw_edges(self, **kwattr)

    def draw_vertex_labels(self, **kwattr):
        mesh_draw_vertex_labels(self, **kwattr)

    def draw_edge_labels(self, **kwattr):
        mesh_draw_edge_labels(self, **kwattr)

    def draw_face_labels(self, **kwattr):
        mesh_draw_face_labels(self, **kwattr)
