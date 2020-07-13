from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.artists import MeshArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__all__ = ['Mesh3gsArtist',]


class Mesh3gsArtist(MeshArtist):
    """Inherits the compas :class:`MeshArtist`, provides functionality for visualisation of 3D graphic statics applications.

    """
    def __init__(self, cell, layer=None):
        super(Mesh3gsArtist, self).__init__(cell, layer=layer)