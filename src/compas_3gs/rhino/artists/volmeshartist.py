from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import VolMeshArtist


__all__ = ['VolMeshArtist']


class VolMeshArtist(VolMeshArtist):
    """A customised `VolMeshArtist` for 3GS `VolMesh`-based data structures."""

    @property
    def diagram(self):
        """The diagram assigned to the artist."""
        return self.volmesh

    @diagram.setter
    def diagram(self, diagram):
        self.volmesh = diagram
