from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

import compas_rhino

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.utilities import get_force_colors_uv
from compas_3gs.utilities import get_force_colors_hf

from compas_rhino.artists import VolMeshArtist
from compas_rhino.artists import NetworkArtist
from compas_rhino.artists import MeshArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
force_layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram = ForceVolMesh()
forcediagram = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = force_layer
forcediagram.attributes['name'] = force_layer

# ------------------------------------------------------------------------------
# 2. make dual network from volmesh (form diagram)
# ------------------------------------------------------------------------------
form_layer = 'form_network'

formdiagram = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer

# move dual_network
offset = 2
width = formdiagram.bounding_box()[1][0] - formdiagram.bounding_box()[0][0]
for vkey in formdiagram.nodes():
    x = formdiagram.node_attribute(vkey, 'x')
    formdiagram.node_attribute(vkey, 'x', x + width * offset)


# ------------------------------------------------------------------------------
# 3. reciprocate
# ------------------------------------------------------------------------------
volmesh_reciprocate(forcediagram,
                    formdiagram,
                    kmax=500,
                    weight=1,
                    edge_min=0.5,
                    edge_max=20,
                    tolerance=0.01)


force_artist = VolMeshArtist(forcediagram, layer=force_layer)
form_artist = NetworkArtist(formdiagram, layer=form_layer)

scaled_cell_artist = MeshArtist(None, layer=force_layer)
prism_artist = MeshArtist(None, layer=force_layer)

force_artist.draw_faces()
form_artist.draw_edges()

# ------------------------------------------------------------------------------
# 4. draw unified diagram
# ------------------------------------------------------------------------------

while True:

    rs.EnableRedraw(True)

    alpha = rs.GetReal('unified diagram scale', minimum=0.01, maximum=1.0)

    if alpha is None:
        break

    if not alpha:
        break

    force_artist.clear_layer()
    form_artist.clear_layer()

    # 1. get colors ------------------------------------------------------------
    hf_color = (0, 0, 0)

    uv_c_dict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)
    hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

    # 2. compute unified diagram geometries ------------------------------------
    # halffaces, prism_faces = volmesh_ud(forcediagram, formdiagram, scale=alpha)
    cells, prisms = volmesh_ud(forcediagram, formdiagram, scale=alpha)

    # 3. draw ------------------------------------------------------------------
    for cell in cells:
        vertices = cells[cell]['vertices']
        faces = cells[cell]['faces']
        compas_rhino.draw_mesh(vertices, faces, layer=force_layer, name=str(cell), color=hf_color, redraw=False)

    # forces = get_force_mags(forcediagram, formdiagram)

    for edge in prisms:
        vertices = prisms[edge]['vertices']
        faces = prisms[edge]['faces']
        compas_rhino.draw_mesh(vertices, faces, layer=force_layer, name=str(edge), color=uv_c_dict[edge], redraw=False)

    form_artist.draw_edges(color=uv_c_dict)
