from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_network_from_volmesh

from compas_3gs_rhino.display import draw_directed_edges_and_halffaces
from compas_3gs_rhino.display import draw_volmesh_boundary_forces
from compas_3gs_rhino.display import draw_network_compression_tension
from compas_3gs_rhino.display import draw_volmesh_face_normals


try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------

forcediagram = rhino_volmesh_from_polysurfaces()


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------

formdiagram = rhino_network_from_volmesh(forcediagram, offset=3)


# ------------------------------------------------------------------------------
# 3. various drawing functions
# ------------------------------------------------------------------------------

# draw_directed_edges_and_halffaces(forcediagram, formdiagram)

# draw_volmesh_boundary_forces(forcediagram, formdiagram, scale=4)

# draw_network_compression_tension(forcediagram, formdiagram)

draw_volmesh_face_normals(forcediagram, scale=2)
