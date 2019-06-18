from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.utilities import i_to_blue

from compas_rhino.artists import MeshArtist

from compas_rhino.helpers import mesh_from_surface
from compas_rhino.helpers import mesh_select_face
from compas_rhino.helpers import mesh_select_faces

from compas_3gs.algorithms import cell_planarise

from compas_3gs.rhino import MeshConduit

from compas_3gs.diagrams import Cell

from compas_3gs.utilities import cell_face_flatness
from compas_3gs.utilities import compare_initial_current

from compas_3gs.rhino import rhino_cell_face_pull_interactive

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make cell from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'cell'

guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
rs.HideObjects(guid)

cell = mesh_from_surface(Cell, guid)
cell.draw()


rhino_cell_face_pull_interactive(cell)
