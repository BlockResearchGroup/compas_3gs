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

from compas_3gs.utilities import get_force_mags
from compas_3gs.utilities import get_force_colors_uv
from compas_3gs.utilities import get_force_colors_hf

from compas_rhino.artists import VolMeshArtist
from compas_rhino.artists import NetworkArtist

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

    # 1. get colors ----------------------------------------------------------------
    hf_color = (0, 0, 0)

    uv_c_dict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)
    hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

    # 2. compute unified diagram geometries ----------------------------------------
    halffaces, prism_faces = volmesh_ud(forcediagram, formdiagram, scale=alpha)

    # 3. halffaces and prisms ------------------------------------------------------
    faces = []
    face_colors = {}
    for hfkey in forcediagram.halffaces():
        vkeys = forcediagram.halfface_vertices(hfkey)
        hf_xyz = [halffaces[hfkey][i] for i in vkeys]
        name = '{}.face.ud.{}'.format(forcediagram.name, hfkey)
        faces.append({'points': hf_xyz,
                      'name': name,
                      'color': hf_color})

    forces = get_force_mags(forcediagram, formdiagram)

    for uv in prism_faces:
        name = '{}.face.ud.prism.{}'.format(forcediagram.name, uv)

        for face in prism_faces[uv]:
            faces.append({'points': face,
                          'name': name,
                          'color': uv_c_dict[uv]})

    # 4. draw ----------------------------------------------------------------------
    force_artist.clear_layer()
    form_artist.clear_layer()

    form_artist.draw_edges(color=uv_c_dict)

    compas_rhino.draw_faces(faces,
                            layer=force_layer,
                            clear=False,
                            redraw=False)
