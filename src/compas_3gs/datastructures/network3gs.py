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


__all__ = ['Network3gs',
           'Network3gsArtist',]


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
            if self.node[vkey]['x_fix'] is False:
                self.node[vkey]['x'] = new_xyz[0]
            # Y
            if self.node[vkey]['y_fix'] is False:
                self.node[vkey]['y'] = new_xyz[1]
            # Z
            if self.node[vkey]['z_fix'] is False:
                self.node[vkey]['z'] = new_xyz[2]
        else:
            self.node[vkey]['x'] = new_xyz[0]
            self.node[vkey]['y'] = new_xyz[1]
            self.node[vkey]['z'] = new_xyz[2]

    # --------------------------------------------------------------------------
    # helpers - edges
    # --------------------------------------------------------------------------

    def edge_vector(self, u, v, unitized=True):
        u_xyz  = self.node_coordinates(u)
        v_xyz  = self.node_coordinates(v)
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


class Network3gsArtist(NetworkArtist):
    """Inherits the compas :class:`NetworkArtist`, provides functionality for visualisation of 3D graphic statics applications.

    """
    def __init__(self, network, layer=None):
        super(Network3gsArtist, self).__init__(network, layer=layer)

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
