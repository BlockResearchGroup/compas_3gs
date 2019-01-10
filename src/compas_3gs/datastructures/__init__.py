"""
********************************************************************************
compas_3gs.datastructures
********************************************************************************

.. currentmodule:: compas_3gs.datastructures




network3gs
==========

.. autosummary::
    :toctree: generated/

    Network3gs


mesh3gs
=======

.. autosummary::
    :toctree: generated/

    Mesh3gs


volmesh3gs
==========

.. autosummary::
    :toctree: generated/

    VolMesh3gs


"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .mesh3gs import *
from .network3gs import *
from .volmesh3gs import *

__all__ = [name for name in dir() if not name.startswith('_')]
