from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.artists import VolMeshArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__all__ = ['VolMesh3gsArtist']


class VolMesh3gsArtist(VolMeshArtist):
    """Inherits the compas :class:`VolMeshArtist`, provides functionality for visualisation of 3D graphic statics applications.

    """
    def __init__(self, cells, layer=None):
        super(VolMesh3gsArtist, self).__init__(cells, layer=layer)