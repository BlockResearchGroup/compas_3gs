"""
********************************************************************************
compas_3gs.diagrams
********************************************************************************

.. currentmodule:: compas_3gs.diagrams


Polyhedral Cell
===============

.. autosummary::
    :toctree: generated/

    EGI
    Cell


Multi-cell Polyhedron
=====================

.. autosummary::
    :toctree: generated/

    FormNetwork
    FormVolMesh
    ForceVolMesh


Cell Network
============

.. autosummary::
    :toctree: generated/

    CellNetwork


"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .egi import *
from .cell import *
from .polyhedral import *
from .disjointed import *

__all__ = [name for name in dir() if not name.startswith('_')]
