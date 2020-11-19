"""
********************************************************************************
compas_3gs.diagrams
********************************************************************************

.. currentmodule:: compas_3gs.diagrams


Polyhedral Cell
===============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    EGI
    Cell

|

____


Multi-cell Polyhedron
=====================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    ForceVolMesh
    FormNetwork
    FormVolMesh

|

____


Cell Network
============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    CellNetwork


"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .egi import *  # noqa: F401 F403
from .cell import *  # noqa: F401 F403
from .polyhedral import *  # noqa: F401 F403
from .disjointed import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
