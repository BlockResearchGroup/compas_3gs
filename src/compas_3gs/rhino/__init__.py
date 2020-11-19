"""
********************************************************************************
compas_3gs.rhino
********************************************************************************

.. currentmodule:: compas_3gs.rhino


Control
================================================================================

Functionalities to enhance user interactivity in Rhino.

Selectors
---------

Various functions for selecting compas_3gs objects in Rhino.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    CellSelector


Modifiers
---------


Inspectors
----------

Dynamic drawing and visualisation functions to enhance selectors and modifers.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    VolmeshVertexInspector
    VolmeshHalffaceInspector
    VolmeshCellInspector
    BiCellInspector


Helpers
-------

Helper functions for selectors, modifiers and inspectors.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    get_initial_point
    get_target_point

|

____

Display
================================================================================

Various drawing functions for Rhino.


Drawing
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    draw_egi_arcs

.. autosummary::
    :toctree: generated/
    :nosignatures:

    draw_cell_force_vectors
    draw_cell_labels
    clear_cell_labels

.. autosummary::
    :toctree: generated/
    :nosignatures:

    draw_network_external_forces
    draw_network_pipes
    draw_directed_hf_and_uv


.. autosummary::
    :toctree: generated/
    :nosignatures:

    draw_volmesh_face_normals

.. autosummary::
    :toctree: generated/
    :nosignatures:

    bake_cells_as_polysurfaces


Modes
-----


Conduits
--------


Helpers
-------


|

____

Wrappers
================================================================================

Wrapper functions specifically for use and visulisation in Rhino.


Algorithms
----------


Constructors
------------


Modifications
-------------


Operations
----------




"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .control import *  # noqa: F401 F403
from .display import *  # noqa: F401 F403
from .wrappers import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
