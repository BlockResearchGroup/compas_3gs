from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormVolMesh

from compas_3gs.algorithms import volmesh_dual_volmesh

from compas_3gs.rhino import draw_cell_labels
from compas_3gs.rhino import draw_directed_hf_and_uv

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

# the layer in which the vomesh should be drawn
layer = 'volmesh'
# construct the volmesh (force diagram) from Rhino polysurfaces
volmesh       = ForceVolMesh()
volmesh       = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# ------------------------------------------------------------------------------
# 2. make dual volmesh (form diagram)
# ------------------------------------------------------------------------------

# the layer in which the dual_volmesh should be drawn
dual_layer   = 'dual_volmesh'
# construct the dual_volmesh (form diagram) from volmesh (force diagram)
dual_volmesh = volmesh_dual_volmesh(volmesh, cls=FormVolMesh)
dual_volmesh.layer = dual_layer
dual_volmesh.attributes['name'] = dual_layer


# ------------------------------------------------------------------------------
# 3. visualise diagrams
# ------------------------------------------------------------------------------

# transform dual_volmesh in x-direction for visualization
offset = 3
x_move = dual_volmesh.bounding_box()[0] * offset
for vkey in dual_volmesh.vertex:
    dual_volmesh.vertex[vkey]['x'] += x_move

# draw volmesh cell labels and dual_volmesh vertex labels
cell_c_dict = get_index_colordict(list(volmesh.cell.keys()))

# draw volmesh
volmesh.draw(layer=dual_layer)
draw_cell_labels(volmesh, color=cell_c_dict)

# draw dual volmesh
dual_volmesh.draw_faces(layer=dual_layer)
dual_volmesh.draw_vertex_labels(color=cell_c_dict)

# draw directed volmesh halffaces and directed dual_volmesh edges
# the corresponding halfface in the volmesh (force diagram) and edges 
# in the dual_volmesh (form diagram) are of the same color
uv_c_dict = get_index_colordict(list(dual_volmesh.edges()))
face_normal_scale = 1.0
draw_directed_hf_and_uv(volmesh,
                        dual_volmesh,
                        uv_color=uv_c_dict,
                        scale=face_normal_scale)
