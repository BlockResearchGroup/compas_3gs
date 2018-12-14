from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_network_from_volmesh
from compas_3gs_rhino.wrappers import rhino_volmesh_reciprocate

from compas_3gs.utilities import pair_hf_to_uv

from compas_3gs_rhino.display import get_force_colors_hf
from compas_3gs_rhino.display import draw_network_external_forces


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
formdiagram = rhino_network_from_volmesh(forcediagram, offset=3)


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
# 3. various drawing functions
# ------------------------------------------------------------------------------

hf_uv_dict = pair_hf_to_uv(forcediagram, formdiagram)

hf_colordict = get_force_colors_hf(forcediagram,
                                   formdiagram,
                                   gradient=True,
                                   boundary=True)

draw_network_external_forces(forcediagram,
                             formdiagram,
                             color=hf_colordict,
                             scale=0.1)

forcediagram.clear_faces()
forcediagram.draw_faces(color=hf_colordict)
