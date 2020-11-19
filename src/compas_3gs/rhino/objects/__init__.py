from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from .forcevolmeshobject import *  # noqa: F401 F403
from .formnetworkobject import *  # noqa: F401 F403
from .volmeshobject import *  # noqa: F401 F403
from .networkobject import *  # noqa: F401 F403

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormNetwork

from .forcevolmeshobject import ForceVolMeshObject
from .formnetworkobject import FormNetworkObject
from .volmeshobject import VolMeshObject
from .networkobject import NetworkObject

VolMeshObject.register(ForceVolMesh, ForceVolMeshObject)
NetworkObject.register(FormNetwork, FormNetworkObject)

__all__ = [name for name in dir() if not name.startswith('_')]
