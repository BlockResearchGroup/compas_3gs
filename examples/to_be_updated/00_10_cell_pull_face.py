from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import mesh_from_surface

from compas_3gs.diagrams import Cell

from compas_3gs.rhino import rhino_cell_face_pull

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
#   1. make cell from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'cell'

guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
rs.HideObjects(guid)

cell = mesh_from_surface(Cell, guid)
cell.draw()

# ------------------------------------------------------------------------------
#   2. pull cell face
# ------------------------------------------------------------------------------
rhino_cell_face_pull(cell)
