from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_3gs.rhino.artists.volmeshartist import VolMeshArtist


__all__ = ['ForceVolMeshArtist']


class ForceVolMeshArtist(VolMeshArtist):
    """Artist for visualizing force diagrams in the Rhino model space."""

    def __init__(self, force, layer=None):
        super(ForceVolMeshArtist, self).__init__(force, layer=layer)

    @property
    def vertex_xyz(self):
        """dict:
        The view coordinates of the mesh vertices.
        The view coordinates default to the actual mesh coordinates.
        """
        if not self._vertex_xyz:
            self._vertex_xyz = {vertex: self.volmesh.vertex_attributes(vertex, 'xy') + [0.0] for vertex in self.volmesh.vertices()}
        return self._vertex_xyz

    @vertex_xyz.setter
    def vertex_xyz(self, vertex_xyz):
        self._vertex_xyz = vertex_xyz
