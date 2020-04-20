from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
from compas_rhino.geometry._constructors import mesh_from_surface
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

layer = 'cell'    # unused variable

# select the polysurface which you create in Rhino
guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)  

# turn Rhino polysurface to a COMPAS single polyhedral cell
cell = mesh_from_surface(Cell, guid)  

# draw the polyhedral cell
cell.draw()  

# hide Rhino polysurface
rs.HideObjects(guid)

## ------------------------------------------------------------------------------
##   2. pull cell face
## ------------------------------------------------------------------------------

# select a cell face and pull  it
rhino_cell_face_pull(cell)  
