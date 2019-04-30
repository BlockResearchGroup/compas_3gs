"""

Make a dual network from a volmesh

author  : Juney Lee
email   : juney.lee@arch.ethz.ch

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormNetwork

from compas_3gs.algorithms import volmesh_dual_network

from compas_3gs.rhino import draw_directed_hf_and_uv
from compas_3gs.rhino import get_index_colordict
from compas_3gs.rhino import draw_cell_labels

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# 1. volmesh from Rhino polysurfaces
layer = 'volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

volmesh       = ForceVolMesh()
volmesh       = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# 2. dual volmesh
dual_layer   = 'dual_network'

dual_network = volmesh_dual_network(volmesh, cls=FormNetwork)
dual_network.layer = dual_layer
dual_network.attributes['name'] = dual_layer


# 3. move dual_network
offset = 3
x_move = dual_network.bounding_box()[0] * offset
for vkey in dual_network.vertex:
    dual_network.vertex[vkey]['x'] += x_move


# 4. draw directed volmesh halffaces and directed dual_volmesh edges
uv_c_dict = get_index_colordict(list(dual_network.edges()))

face_normal_scale = 1.0
volmesh.draw_edges()
draw_directed_hf_and_uv(volmesh,
                        dual_network,
                        uv_color=uv_c_dict,
                        scale=face_normal_scale)


# 5. draw volmesh cell labels and dual network vertex labels
cell_c_dict = get_index_colordict(list(volmesh.cell.keys()))

draw_cell_labels(volmesh, color=cell_c_dict)
dual_network.draw_vertex_labels(color=cell_c_dict)
