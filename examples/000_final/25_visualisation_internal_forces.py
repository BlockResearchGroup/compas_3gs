from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import random

import compas

import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import draw_cell_labels
from compas_3gs.rhino import get_force_mags
from compas_3gs.rhino import get_index_colordict
from compas_3gs.rhino import get_force_colors_uv
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
# 3. get internal forces and colors
# ------------------------------------------------------------------------------
drawing_scale = 0.1

# 1. colors and force magnitudes -----------------------------------------------
uv_f_dict = get_force_mags(forcediagram, formdiagram)
uv_c_dict = get_force_colors_uv(forcediagram, formdiagram, gradient=True)


# ------------------------------------------------------------------------------
# 4. draw internal forces
# ------------------------------------------------------------------------------

# pick formdiagram vertices to draw internal forcees at
vkeys = random.sample(formdiagram.vertex, k=int(len(formdiagram.vertex) / 5))

internal_forces = []

for u in vkeys:
    for v in formdiagram.vertex_neighbors(u):

        vec   = formdiagram.edge_direction(u, v)
        u_xyz = formdiagram.vertex_coordinates(u)

        if (u, v) in uv_f_dict:
            force = uv_f_dict[(u, v)]
            color = uv_c_dict[(u, v)]

        else:
            force = uv_f_dict[(v, u)]
            color = uv_c_dict[(v, u)]

        v_xyz = add_vectors(u_xyz, scale_vector(vec, abs(force) * drawing_scale))

        sp = u_xyz
        ep = v_xyz
        if force < 0 :  # if compression
            sp = v_xyz
            ep = u_xyz

        internal_forces.append({
            'start': sp,
            'end'  : ep,
            'color': color,
            'arrow': 'end',
            'layer': formdiagram.layer,
            'name' : '{}.edge.force.{}-{}'.format(formdiagram.name, u, v)})

compas_rhino.draw_lines(internal_forces)

# 3. draw forcediagram ---------------------------------------------------------
boundary_halffaces = forcediagram.halffaces_on_boundary()
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

faces_to_draw = []
for vkey in vkeys:
    cell_halffaces = forcediagram.cell_halffaces(vkey)
    for fkey in cell_halffaces:
        if fkey not in boundary_halffaces:
            faces_to_draw.append(fkey)

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=faces_to_draw, color=hf_c_dict)

# 5 draw volmesh cell and network vertex labels --------------------------------
cell_label_colordict = get_index_colordict(vkeys)

draw_cell_labels(forcediagram, ckeys=vkeys, color=cell_label_colordict)
textdict = {key: str(key) for key in vkeys}
formdiagram.draw_vertex_labels(text=textdict, color=cell_label_colordict)
