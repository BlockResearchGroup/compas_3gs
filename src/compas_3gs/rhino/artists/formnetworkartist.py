from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_3gs.rhino.artists.networkartist import NetworkArtist


__all__ = ['FormNetworkArtist']


class FormNetworkArtist(NetworkArtist):
    """Artist for visualizing force diagrams in the Rhino model space."""

    def __init__(self, form, layer=None):
        super(FormNetworkArtist, self).__init__(form, layer=layer)

    @property
    def node_xyz(self):
        """dict:
        The view coordinates of the network vertices.
        The view coordinates default to the actual network coordinates.
        """
        if not self._node_xyz:
            self._node_xyz = {node: self.network.node_attributes(node, 'xyz') + [0.0] for node in self.network.nodes()}
        return self._node_xyz

    @node_xyz.setter
    def node_xyz(self, node_xyz):
        self._node_xyz = node_xyz
