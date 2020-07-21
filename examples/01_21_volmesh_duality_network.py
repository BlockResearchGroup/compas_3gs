from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh, FormNetwork
from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.rhino import draw_directed_hf_and_uv, draw_cell_labels
from compas_3gs.utilities import get_index_colordict

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces (force diagram)
# ------------------------------------------------------------------------------

# select Rhino polysurfaces
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

# the layer in which the volmesh should be drawn
layer = 'volmesh'
# construct the volmesh (force diagram) from Rhino polysurfaces
volmesh       = ForceVolMesh()
volmesh       = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------

# the layer in which the dual_network should be drawn
dual_layer   = 'dual_network'
# construct the dual_network (form diagram) from volmesh (force diagram)
dual_network = volmesh_dual_network(volmesh, cls=FormNetwork)
dual_network.layer = dual_layer
dual_network.attributes['name'] = dual_layer


# ------------------------------------------------------------------------------
# 3. visualise diagrams
# ------------------------------------------------------------------------------

# transform dual_network in x-direction for visualization
offset = 3
x_move = dual_network.bounding_box()[0] * offset
for vkey in dual_network.node:
    dual_network.node[vkey]['x'] += x_move


# draw directed volmesh halffaces and directed dual_volmesh edges
# the corresponding halfface in the volmesh (force diagram) and
# edges in the dual_network (form diagram) are of the same color
uv_c_dict = get_index_colordict(list(dual_network.edges()))
face_normal_scale = 1.0
volmesh.draw_edges(layer=layer)
draw_directed_hf_and_uv(volmesh,
                        dual_network,
                        uv_color=uv_c_dict,
                        scale=face_normal_scale)


# draw volmesh cell labels and dual network vertex labels
cell_c_dict = get_index_colordict(list(volmesh.cell.keys()))
draw_cell_labels(volmesh, color=cell_c_dict)
dual_network.draw_vertex_labels(layer=dual_layer, color=cell_c_dict)
