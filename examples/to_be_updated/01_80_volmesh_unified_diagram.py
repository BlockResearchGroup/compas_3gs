from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

import compas_rhino

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.utilities import get_force_mags
from compas_3gs.utilities import get_force_colors_uv
from compas_3gs.utilities import get_force_colors_hf

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
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
# 4. draw unified diagram
# ------------------------------------------------------------------------------
alpha = rs.GetReal('unified diagram scale', 1, 0.01, 1.0)

hfkeys = forcediagram.halfface.keys()

# 1. get colors ----------------------------------------------------------------
hf_color = (0, 0, 0)

uv_c_dict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)
# uv_c_dict = get_index_colordict(list(formdiagram.edges()))
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

# 2. compute unified diagram geometries ----------------------------------------
halffaces, prism_faces = volmesh_ud(forcediagram, formdiagram, scale=alpha)

# 3. halffaces and prisms ------------------------------------------------------
faces = []
for hfkey in hfkeys:
    vkeys  = forcediagram.halfface[hfkey]
    hf_xyz = [halffaces[hfkey][i] for i in vkeys]
    name   = '{}.face.ud.{}'.format(forcediagram.name, hfkey)
    faces.append({'points': hf_xyz,
                  'name'  : name,
                  'color' : hf_color})

forces = get_force_mags(forcediagram, formdiagram)

for uv in prism_faces:
    name  = '{}.face.ud.prism.{}'.format(forcediagram.name, uv)

    for face in prism_faces[uv]:
        faces.append({'points': face,
                      'name'  : name,
                      'color' : uv_c_dict[uv]})

# 4. draw ----------------------------------------------------------------------
formdiagram.draw_edges(color=uv_c_dict)

compas_rhino.draw_faces(faces,
                        layer=forcediagram.layer,
                        clear=False,
                        redraw=False)
