from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import random

import compas

import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.rhino import draw_cell_labels
from compas_3gs.rhino import get_force_mags
from compas_3gs.rhino import get_index_colordict
from compas_3gs.rhino import get_force_colors_uv
from compas_3gs.rhino import get_force_colors_hf

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram       = ForceVolMesh()
forcediagram       = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer


# ------------------------------------------------------------------------------
# 2. pick cell
# ------------------------------------------------------------------------------
cell_colors = get_index_colordict(forcediagram.cell)

forcediagram.draw_edges()
forcediagram.draw_faces()
draw_cell_labels(forcediagram)
rs.EnableRedraw(True)

