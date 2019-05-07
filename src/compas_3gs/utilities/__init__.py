"""
********************************************************************************
compas_3gs.utilities
********************************************************************************

.. currentmodule:: compas_3gs.utilities


Geometry
================================================================================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    resultant_vector
    datastructure_centroid


Topology
================================================================================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    pair_hf_to_uv
    pair_uv_to_hf


"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .geometry import *
from .other import *
from .topology import *

__all__ = [name for name in dir() if not name.startswith('_')]
