from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import get_index_colordict
from compas_3gs.rhino import get_force_colors_hf

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
layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram       = ForceVolMesh()
forcediagram       = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer


# ------------------------------------------------------------------------------
# 2. make dual network from volmesh (form diagram)
# ------------------------------------------------------------------------------
layer = 'form_network'

formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = layer
formdiagram.attributes['name'] = layer

x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.vertex:
    formdiagram.vertex[vkey]['x'] += x_move


# ------------------------------------------------------------------------------
# 3. reciprocate
# ------------------------------------------------------------------------------
volmesh_reciprocate(forcediagram,
                    formdiagram,
                    kmax=1000,
                    weight=1,
                    edge_min=0.5,
                    edge_max=20,
                    tolerance=0.01)


# ------------------------------------------------------------------------------
# 4. visualisation - color id
# ------------------------------------------------------------------------------
uv_c_dict = get_index_colordict(list(formdiagram.edges()))
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

faces_to_draw = [fkey for fkey in forcediagram.faces() if fkey in forcediagram.halffaces_interior()]

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=faces_to_draw, color=hf_c_dict)

formdiagram.clear()
formdiagram.draw_edges(color=uv_c_dict)
