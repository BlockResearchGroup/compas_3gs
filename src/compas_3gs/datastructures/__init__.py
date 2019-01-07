"""
********************************************************************************
compas_3gs.datastructures
********************************************************************************

.. currentmodule:: compas_3gs.datastructures


"""


from __future__ import absolute_import

from .mesh3gs import *
from .network3gs import *
from .volmesh3gs import *

__all__ = []

__all__ += mesh3gs.__all__
__all__ += network3gs.__all__
__all__ += volmesh3gs.__all__
