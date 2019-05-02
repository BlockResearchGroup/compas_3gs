from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
#   1. make / set layer
# ------------------------------------------------------------------------------
layer = 'force_volmesh'


# ------------------------------------------------------------------------------
#   2. select rhino polysurfaces
# ------------------------------------------------------------------------------
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)


# ------------------------------------------------------------------------------
#   3. make volmesh
# ------------------------------------------------------------------------------
volmesh       = ForceVolMesh()
volmesh       = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# ------------------------------------------------------------------------------
#   4. draw volmesh
# ------------------------------------------------------------------------------
volmesh.draw(layer=layer)
