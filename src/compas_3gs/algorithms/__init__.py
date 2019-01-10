"""
********************************************************************************
compas_3gs.algorithms
********************************************************************************

.. currentmodule:: compas_3gs.algorithms


Arearisation
============

.. autosummary::
    :toctree: generated/

    mesh_arearise


Duality
=======

.. autosummary::
    :toctree: generated/

    volmesh_dual_volmesh
    volmesh_dual_network


EGI
===

.. autosummary::
    :toctree: generated/

    egi_from_vectors


Planarisation
=============

.. autosummary::
    :toctree: generated/

    volmesh_planarise


Relaxation
==========

.. autosummary::
    :toctree: generated/


Reciprocation
=============

.. autosummary::
    :toctree: generated/

    volmesh_reciprocate


Unified Diagram
===============

.. autosummary::
    :toctree: generated/

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
