"""
********************************************************************************
compas_3gs.algorithms
********************************************************************************

.. currentmodule:: compas_3gs.algorithms


EGI
===

.. autosummary::
    :toctree: generated/
    :nosignatures:

    egi_from_vectors


____


Duality
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    volmesh_dual_volmesh
    volmesh_dual_network


____


Reciprocation
=============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    volmesh_reciprocate


____


Planarisation
=============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    volmesh_planarise


Arearisation
============


.. autosummary::
    :toctree: generated/
    :nosignatures:

    cell_arearise_face


____


Unified Diagram
===============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    volmesh_ud
    cellnetwork_ud

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .arearisation import *  # noqa: F401 F403
from .duality import *  # noqa: F401 F403
from .egi import *  # noqa: F401 F403
from .other import *  # noqa: F401 F403
from .planarisation import *  # noqa: F401 F403
from .reciprocation import *  # noqa: F401 F403
from .unifieddiagram import *  # noqa: F401 F403


__all__ = [name for name in dir() if not name.startswith('_')]
