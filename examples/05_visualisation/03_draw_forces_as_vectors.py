from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_3gs_rhino.display

from compas_rhino.selectors import VertexSelector

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_network_from_volmesh
from compas_3gs_rhino.wrappers import rhino_volmesh_reciprocate

from compas_3gs_rhino.display import draw_network_external_forces
from compas_3gs_rhino.display import draw_network_internal_forces
from compas_3gs_rhino.display import draw_volmesh_cells

from compas_3gs_rhino.display import get_force_colors_hf


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
# weight = rs.GetReal(
#     "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)
weight = 1


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
# 5. select vertices
# ------------------------------------------------------------------------------
vkeys = VertexSelector.select_vertices(formdiagram)


# ------------------------------------------------------------------------------
# 6. various drawing functions
# ------------------------------------------------------------------------------
drawing_scale = 0.05

hf_colordict = get_force_colors_hf(forcediagram,
                                   formdiagram,
                                   gradient=True,
                                   boundary=True)

formdiagram.clear()
formdiagram.draw_vertices(keys=vkeys)

draw_network_external_forces(forcediagram,
                             formdiagram,
                             vkeys=vkeys,
                             color=hf_colordict,
                             scale=drawing_scale)

draw_network_internal_forces(forcediagram,
                             formdiagram,
                             vkeys=vkeys,
                             gradient=True,
                             scale=drawing_scale)

forcediagram.clear()
draw_volmesh_cells(forcediagram, ckeys=vkeys, color=hf_colordict)
