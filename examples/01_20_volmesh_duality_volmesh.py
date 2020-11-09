from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormVolMesh

from compas_3gs.algorithms import volmesh_dual_volmesh

from compas_3gs.rhino import draw_directed_hf_and_uv

from compas_3gs.utilities import get_index_colordict

from compas_rhino.artists import VolMeshArtist


try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces (force diagram)
# ------------------------------------------------------------------------------
layer = 'volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

volmesh = ForceVolMesh()
volmesh = volmesh_from_polysurfaces(volmesh, guids)
volmesh.layer = layer
volmesh.attributes['name'] = layer


# ------------------------------------------------------------------------------
# 2. make dual volmesh (form diagram)
# ------------------------------------------------------------------------------
dual_layer = 'dual_volmesh'

dual_volmesh = volmesh_dual_volmesh(volmesh, cls=FormVolMesh)
dual_volmesh.layer = dual_layer
dual_volmesh.attributes['name'] = dual_layer

# move dual_network
offset = 2
width = dual_volmesh.bounding_box()[1][0] - dual_volmesh.bounding_box()[0][0]
for vkey in dual_volmesh.nodes():
    x = dual_volmesh.node_attribute(vkey, 'x')
    dual_volmesh.node_attribute(vkey, 'x', x + width * offset)


# ------------------------------------------------------------------------------
# 3. visualise diagrams
# ------------------------------------------------------------------------------
force_artist = VolMeshArtist(volmesh)
form_artist = VolMeshArtist(dual_volmesh)

# draw volmesh cell labels and dual_volmesh vertex labels
cell_c_dict = get_index_colordict(list(volmesh.cells()))

# draw volmesh
force_artist.draw_edges()
force_artist.draw_celllabels(color=cell_c_dict)

# draw dual volmesh
form_artist.draw_faces()
form_artist.draw_vertexlabels(color=cell_c_dict)

# draw directed volmesh halffaces and directed dual_volmesh edges
uv_c_dict = get_index_colordict(list(dual_volmesh.edges()))

face_normal_scale = 1.0
draw_directed_hf_and_uv(volmesh,
                        dual_volmesh,
                        uv_color=uv_c_dict,
                        scale=face_normal_scale)
