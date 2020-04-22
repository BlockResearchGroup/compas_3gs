from __future__ import print_function

from compas.datastructures import Network

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector

from compas_rhino.artists import NetworkArtist

from compas_3gs.utilities import datastructure_centroid


__author__     = 'Juney Lee'
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
    # misc
    # --------------------------------------------------------------------------

    def bounding_box(self):

        xyz = [self.node_coordinates(vkey) for vkey in self.node]

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

    def draw(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        # artist.draw() # NetworkArtist.draw() raise NotImplementedError
        artist.draw_edges(**kwattr)
        artist.draw_nodes(**kwattr)

    def clear(self, layer=None):
        artist = NetworkArtist(self, layer)
        artist.clear()

    def draw_vertices(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        artist.draw_nodes(**kwattr)

    def draw_edges(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        artist.draw_edges(**kwattr)

    def clear_edges(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        artist.clear_edges(**kwattr)

    def draw_vertex_labels(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        artist.draw_nodelabels(**kwattr)

    def draw_edge_labels(self, layer=None, **kwattr):
        artist = NetworkArtist(self, layer)
        artist.draw_edgelabels(**kwattr)


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
