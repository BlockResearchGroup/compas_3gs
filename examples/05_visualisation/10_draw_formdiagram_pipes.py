from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_network_from_volmesh
from compas_3gs_rhino.wrappers import rhino_volmesh_reciprocate

from compas_3gs_rhino.display import draw_network_pipes

from compas_3gs_rhino.display import get_force_colors_uv


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
# 5. draw
# ------------------------------------------------------------------------------
uv_colordict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)

drawing_scale = 0.02

draw_network_pipes(forcediagram,
                   formdiagram,
                   color=uv_colordict,
                   scale=drawing_scale)
