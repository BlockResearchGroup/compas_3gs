"""
********************************************************************************
compas_3gs.algorithms
********************************************************************************

.. currentmodule:: compas_3gs.algorithms


Duality
=======

.. autosummary::
    :toctree: generated/

    volmesh_dual_volmesh
    volmesh_dual_network

Planarisation
=============

.. autosummary::
    :toctree: generated/

    volmesh_planarise_faces

Reciprocation
=============

.. autosummary::
    :toctree: generated/

    volmesh_reciprocate

"""

from __future__ import absolute_import

from .arearisation import *
from .duality import *
from .egi import *
from .planarisation import *
from .reciprocation import *

from . import arearisation
from . import duality
from . import egi
from . import planarisation
from . import reciprocation

__all__ = []

__all__ += arearisation.__all__
__all__ += duality.__all__
__all__ += egi.__all__
__all__ += planarisation.__all__
__all__ += reciprocation.__all__
