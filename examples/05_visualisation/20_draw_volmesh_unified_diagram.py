from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs.rhino import rhino_volmesh_from_polysurfaces
from compas_3gs.rhino import rhino_network_from_volmesh
from compas_3gs.rhino import rhino_volmesh_reciprocate

from compas_3gs.rhino import draw_volmesh_UD

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
forcediagram = rhino_volmesh_from_polysurfaces()


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------
formdiagram = rhino_network_from_volmesh(forcediagram, offset=2)


# ------------------------------------------------------------------------------
# 3. get reciprocation weight factor
# ------------------------------------------------------------------------------
weight = rs.GetReal(
    "Enter weight factor : 1 = form only... 0 = force only...", 1.0, 0)


# ------------------------------------------------------------------------------
# 4. reciprocate
# ------------------------------------------------------------------------------
rhino_volmesh_reciprocate(forcediagram,
                          formdiagram,
                          kmax=2000,
                          weight=weight,
                          edge_min=0.5,
                          edge_max=20,
                          fix_vkeys=[],
                          tolerance=0.001,
                          refreshrate=5)


# ------------------------------------------------------------------------------
# 5. unified diagram
# ------------------------------------------------------------------------------

ud_scale = rs.GetReal(
    "Enter unified diagram scale: 1 = form diagram ...", 1.0, 0)

forcediagram.clear()
draw_volmesh_UD(forcediagram, formdiagram, scale=ud_scale)
