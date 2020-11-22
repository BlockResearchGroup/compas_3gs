from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rhino.objects import NetworkObject


__all__ = ['NetworkObject']


class NetworkObject(NetworkObject):
    """A customised `NetworkArtist` for 3GS `Network`-based data structures."""

    @property
    def diagram(self):
        """The diagram associated with the object."""
        return self.network

    @diagram.setter
    def diagram(self, diagram):
        self.network = diagram

    def select_node(self, message="Select vertices."):
        """Select vertices of the volmesh.

        Returns
        -------
        list
            A list of vertex identifiers.
        """
        guid = compas_rhino.select_point(message=message)
        if guid and guid in self.guid_node:
            return self.guid_node[guid]

    select_vertex = select_node
    select_vertices = NetworkObject.select_nodes
