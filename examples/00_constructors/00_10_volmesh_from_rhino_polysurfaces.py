from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.datastructures import Mesh

from compas.geometry import distance_point_point

from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import EGI
from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# make / set layer
# ------------------------------------------------------------------------------
layer = 'force_volmesh'


# ------------------------------------------------------------------------------
# select rhino polysurfaces
# ------------------------------------------------------------------------------
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)


# ------------------------------------------------------------------------------
# make volmesh
# ------------------------------------------------------------------------------
volmesh       = ForceVolMesh()
volmesh       = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# ------------------------------------------------------------------------------
# draw volmesh
# ------------------------------------------------------------------------------
volmesh.draw(layer=layer)
