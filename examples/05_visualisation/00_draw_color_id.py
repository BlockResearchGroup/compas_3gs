from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_network_from_volmesh
from compas_3gs_rhino.wrappers import rhino_volmesh_reciprocate

from compas_3gs.utilities import pair_hf_to_uv

from compas_3gs_rhino.display.helpers import get_index_colordict
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
# 3. various drawing functions
# ------------------------------------------------------------------------------
uv_c_dict = get_index_colordict(list(formdiagram.edges()))
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=hf_c_dict, color=hf_c_dict)

formdiagram.clear()
formdiagram.draw_edges(color=uv_c_dict)
