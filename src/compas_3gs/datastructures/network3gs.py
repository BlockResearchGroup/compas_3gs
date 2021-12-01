from __future__ import print_function

from compas.datastructures import Network

from compas.geometry import bounding_box

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector

from compas_3gs.utilities import datastructure_centroid


__all__ = ['Network3gs']


class Network3gs(Network):
    """Inherits and extends the compas Network class, such that it is more suitable for 3D graphic statics applications.

    Primarily used for polyhedral (and possibly non-polyhedral) form diagrams.

    """

    def __init__(self):
        super(Network3gs, self).__init__()
        self.dual = None
        self.default_edge_attributes.update({
            'lmin': 0.0,
            'lmax': 1e+7,

            '_a': 0.0,
        })

    # --------------------------------------------------------------------------
    #   inherited functions
    # --------------------------------------------------------------------------

    datastructure_centroid = datastructure_centroid
    vertex_coordinates = Network.node_coordinates
    vertex_neighbors = Network.neighbors
    vertices = Network.nodes

    # --------------------------------------------------------------------------
    # misc
    # --------------------------------------------------------------------------

    def bounding_box(self):

        xyz = self.nodes_attributes('xyz', keys=list(self.nodes()))

        # x_sorted = sorted(xyz, key=lambda k: k[0])
        # y_sorted = sorted(xyz, key=lambda k: k[1])
        # z_sorted = sorted(xyz, key=lambda k: k[2])

        # x = abs(x_sorted[0][0] - x_sorted[-1][0])
        # y = abs(y_sorted[0][1] - y_sorted[-1][1])
        # z = abs(z_sorted[0][2] - z_sorted[-1][2])

        return bounding_box(xyz)

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, node, new_xyz, constrained=True):

        if constrained:
            # X
            if self.node_attribute(node, 'x_fix') is False:
                self.node_attribute(node, 'x', new_xyz[0])
            # Y
            if self.node_attribute(node, 'y_fix') is False:
                self.node_attribute(node, 'y', new_xyz[1])
            # Z
            if self.node_attribute(node, 'z_fix') is False:
                self.node_attribute(node, 'z', new_xyz[2])
        else:
            self.node_attribute(node, 'x', new_xyz[0])
            self.node_attribute(node, 'y', new_xyz[1])
            self.node_attribute(node, 'z', new_xyz[2])

    # --------------------------------------------------------------------------
    # helpers - edges
    # --------------------------------------------------------------------------

    def edge_vector(self, u, v, unitized=True):
        u_xyz = self.vertex_coordinates(u)
        v_xyz = self.vertex_coordinates(v)
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

    # def draw(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.draw_edges(**kwattr)
    #     artist.draw_nodes(**kwattr)

    # def clear(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.clear_by_name()
    #     artist.clear_layer()

    # def draw_nodes(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.draw_nodes(**kwattr)

    # def draw_edges(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.draw_edges(**kwattr)

    # def draw_vertexlabels(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.draw_vertexlabels(**kwattr)

    # def draw_edgelabels(self, **kwattr):
    #     artist = NetworkArtist(self)
    #     artist.draw_edgelabels(**kwattr)


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
