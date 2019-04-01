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


____


Arearisation
============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    mesh_arearise


____


Relaxation
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

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

from .arearisation import *
from .duality import *
from .egi import *
from .planarisation import *
from .reciprocation import *
from .relaxation import *
from .unifieddiagram import *

__all__ = [name for name in dir() if not name.startswith('_')]
