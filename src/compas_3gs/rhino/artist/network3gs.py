from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.artists import NetworkArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__all__ = ['Network3gsArtist',]


class Network3gsArtist(NetworkArtist):
    """Inherits the compas :class:`NetworkArtist`, provides functionality for visualisation of 3D graphic statics applications.

    """
    def __init__(self, network, layer=None):
        super(Network3gsArtist, self).__init__(network, layer=layer)
