from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import NetworkArtist


__all__ = ['NetworkArtist']


class NetworkArtist(NetworkArtist):
    """A customised `NetworkArtist` for 3GS `Network`-based data structures."""

    @property
    def diagram(self):
        """The diagram assigned to the artist."""
        return self.network

    @diagram.setter
    def diagram(self, diagram):
        self.network = diagram
