from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.rhino import draw_cell_labels

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
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

forcediagram.draw()
forcediagram.draw_vertex_labels()
draw_cell_labels(forcediagram)
