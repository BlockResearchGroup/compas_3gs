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

from compas_3gs.rhino import get_force_colors_uv
from compas_3gs.rhino import get_force_colors_hf

from compas_3gs.utilities import pair_uv_to_hf

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

x_move = formdiagram.bounding_box()[0] * 3
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
# 4. visualisation - pipes
# ------------------------------------------------------------------------------
uv_c_dict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

uv_hf_dict = pair_uv_to_hf(formdiagram, forcediagram)

faces_to_draw = [fkey for fkey in forcediagram.faces() if fkey in forcediagram.halffaces_interior()]

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=faces_to_draw, color=hf_c_dict)

drawing_scale = 0.01
cylinders = []
for uv in formdiagram.edges():
    cylinders.append({
        'start' : formdiagram.vertex_coordinates(uv[0]),
        'end'   : formdiagram.vertex_coordinates(uv[1]),
        'radius': forcediagram.halfface_oriented_area(uv_hf_dict[uv]) * drawing_scale,
        'color' : uv_c_dict[uv],
        'layer' : formdiagram.layer,
        'name'  : '{}.edge.pipes.{}'.format(formdiagram.name, uv)})

compas_rhino.draw_cylinders(cylinders, cap=True)
