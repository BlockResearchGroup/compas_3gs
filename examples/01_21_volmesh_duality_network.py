from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.diagrams import FormNetwork

from compas_3gs.algorithms import volmesh_dual_network

from compas_3gs.rhino import draw_directed_hf_and_uv

from compas_3gs.utilities import get_index_colordict

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_rhino.artists import NetworkArtist
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
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------
dual_layer = 'dual_network'

dual_network = volmesh_dual_network(volmesh, cls=FormNetwork)
dual_network.layer = dual_layer
dual_network.attributes['name'] = dual_layer

# move dual_network
offset = 3
width = dual_network.bounding_box()[1][0] - dual_network.bounding_box()[0][0]
for vkey in dual_network.nodes():
    x = dual_network.node_attribute(vkey, 'x')
    dual_network.node_attribute(vkey, 'x', x + width * offset)


# ------------------------------------------------------------------------------
# 3. visualise diagrams
# ------------------------------------------------------------------------------
force_artist = VolMeshArtist(volmesh)
form_artist = NetworkArtist(dual_network)

# draw volmesh cell labels and dual network vertex labels
cell_c_dict = get_index_colordict(list(volmesh.cells()))

# draw volmesh
force_artist.draw_edges()
force_artist.draw_celllabels(color=cell_c_dict)

# draw dual network
form_artist.draw_nodelabels(color=cell_c_dict)

# draw directed volmesh halffaces and directed dual_volmesh edges
uv_c_dict = get_index_colordict(list(dual_network.edges()))

face_normal_scale = 1.0
draw_directed_hf_and_uv(volmesh,
                        dual_network,
                        uv_color=uv_c_dict,
                        scale=face_normal_scale)
