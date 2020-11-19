"""
********************************************************************************
compas_3gs.datastructures
********************************************************************************

.. currentmodule:: compas_3gs.datastructures


network3gs
==========

inherits compas mesh and adds these functions...

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Network3gs

|

____


mesh3gs
=======

inherits compas mesh and adds these functions...

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Mesh3gs

|

____


volmesh3gs
==========

inherits compas mesh and adds these functions...

.. autosummary::
    :toctree: generated/
    :nosignatures:

    VolMesh3gs

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .mesh3gs import *  # noqa: F401 F403
from .network3gs import *  # noqa: F401 F403
from .volmesh3gs import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
