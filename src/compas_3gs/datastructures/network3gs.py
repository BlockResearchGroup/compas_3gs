from __future__ import print_function

from compas.datastructures import Network

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector

from compas_rhino.helpers.network import network_draw
from compas_rhino.helpers.network import network_draw_vertices
from compas_rhino.helpers.network import network_draw_edges
from compas_rhino.helpers.network import network_draw_vertex_labels
from compas_rhino.helpers.network import network_draw_edge_labels

from compas_rhino.artists import NetworkArtist

from compas_3gs.utilities import datastructure_centroid


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['Network3gs']


class Network3gs(Network):
    """Inherits and extends the compas Network class, such that it is more suitable for 3D graphic statics applications.

    Primarily used for polyhedral (and possibly non-polyhedral) form diagrams.

    """

    def __init__(self):
        super(Network3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   inherited functions
    # --------------------------------------------------------------------------

    datastructure_centroid = datastructure_centroid

    # --------------------------------------------------------------------------
    # iterators
    # --------------------------------------------------------------------------

    # def edges_iter(self, data=False):
    #     for u in self.edge:
    #         for v in self.edge[u]:
    #             if data:
    #                 yield u, v, self.edge[u][v]
    #             else:
    #                 yield u, v

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

    # def initialize_data(self):
    #     for vkey in self.vertex:
    #         self.update_v_data(vkey)
    #     for u, v in self.edges():
    #         self.update_e_data(u, v)

    # --------------------------------------------------------------------------
    # misc
    # --------------------------------------------------------------------------

    def bounding_box(self):

        xyz = [self.vertex_coordinates(vkey) for vkey in self.vertex]

        x_sorted = sorted(xyz, key=lambda k: k[0])
        y_sorted = sorted(xyz, key=lambda k: k[1])
        z_sorted = sorted(xyz, key=lambda k: k[2])

        x = abs(x_sorted[0][0] - x_sorted[-1][0])
        y = abs(y_sorted[0][1] - y_sorted[-1][1])
        z = abs(z_sorted[0][2] - z_sorted[-1][2])

        return x, y, z



    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, vkey, new_xyz, constrained=True):
        if constrained:
            # X
            if self.vertex[vkey]['x_fix'] is False:
                self.vertex[vkey]['x'] = new_xyz[0]
            # Y
            if self.vertex[vkey]['y_fix'] is False:
                self.vertex[vkey]['y'] = new_xyz[1]
            # Z
            if self.vertex[vkey]['z_fix'] is False:
                self.vertex[vkey]['z'] = new_xyz[2]
        else:
            self.vertex[vkey]['x'] = new_xyz[0]
            self.vertex[vkey]['y'] = new_xyz[1]
            self.vertex[vkey]['z'] = new_xyz[2]

    # --------------------------------------------------------------------------
    # helpers - edges
    # --------------------------------------------------------------------------

    def edge_vector(self, u, v, unitized=True):
        u_xyz  = self.vertex_coordinates(u)
        v_xyz  = self.vertex_coordinates(v)
        vector = subtract_vectors(v_xyz, u_xyz)
        if unitized:
            return normalize_vector(vector)
        return vector

    def edge_avg_length(self):
        sum_length = 0
        edge_count = 0
        for u, v in self.edges_iter():
            edge_vector = self.edge_vector(u, v, unitized=False)
            sum_length += length_vector(edge_vector)
            edge_count += 1
        return sum_length / edge_count


    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        network_draw(self, **kwattr)

    def clear(self, **kwattr):
        artist = NetworkArtist(self)
        artist.clear()
        # artist.clear_layer()

    def draw_vertices(self, **kwattr):
        network_draw_vertices(self, **kwattr)

    def draw_edges(self, **kwattr):
        network_draw_edges(self, **kwattr)

    def clear_edges(self, **kwattr):
        artist = NetworkArtist(self, **kwattr)
        artist.clear_edges(**kwattr)


    def draw_vertex_labels(self, **kwattr):
        network_draw_vertex_labels(self, **kwattr)

    def draw_edge_labels(self, **kwattr):
        network_draw_edge_labels(self, **kwattr)
