from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_rhino import unload_modules  
unload_modules("compas")

import compas

from compas_rhino.geometry import RhinoSurface
from compas_3gs.diagrams import Cell
from compas_3gs.rhino import rhino_cell_face_pull
from compas_3gs.datastructures import Mesh3gsArtist


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
# select the polysurface which you create in Rhino
guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
# turn Rhino polysurface to a COMPAS single polyhedral cell
cell = RhinoSurface.from_guid(guid).brep_to_compas(cls=Cell())

# draw the polyhedral cell
layer = 'cell' 
cellartist = Mesh3gsArtist(cell, layer=layer)
cellartist.draw()  
# hide Rhino polysurface
rs.HideObjects(guid)


## ------------------------------------------------------------------------------
##   2. pull cell face
## ------------------------------------------------------------------------------
# select a cell face and pull it along its normal vector
rhino_cell_face_pull(cell)  
