from __future__ import absolute_import
from __future__ import print_function
from __future__ import division


from .formnetworkartist import *  # noqa: F401 F403
from .forcevolmeshartist import *  # noqa: F401 F403
from .networkartist import *  # noqa: F401 F403
from .volmeshartist import *  # noqa: F401 F403

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormNetwork

from .forcevolmeshartist import ForceVolMeshArtist
from .formnetworkartist import FormNetworkArtist
from .volmeshartist import VolMeshArtist
from .networkartist import NetworkArtist

VolMeshArtist.register(ForceVolMesh, ForceVolMeshArtist)
NetworkArtist.register(FormNetwork, FormNetworkArtist)


__all__ = [name for name in dir() if not name.startswith('_')]
