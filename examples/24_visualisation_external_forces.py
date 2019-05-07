from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

import compas_rhino

from compas.geometry import scale_vector
from compas.geometry import add_vectors

from compas.utilities import i_to_green

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.utilities import valuedict_to_colordict

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
# 4. visualisation - external forces
# ------------------------------------------------------------------------------

hfkeys = forcediagram.halffaces_on_boundary()

# 1. delete any existing boundary forces ---------------------------------------
name = '*.edge.loads.*'
compas_rhino.delete_objects(compas_rhino.get_objects(name=name))


# 3. get hf areas and colors ---------------------------------------------------
hf_areas  = {hfkey: forcediagram.halfface_oriented_area(hfkey) for hfkey in hfkeys}
hf_c_dict = valuedict_to_colordict(hf_areas, color_scheme=i_to_green)


# 4. exteranl forces to draw ---------------------------------------------------
drawing_scale = 0.2
lines = []
for hfkey in hfkeys:
    ckey   = forcediagram.halfface_cell(hfkey)
    normal = forcediagram.halfface_oriented_normal(hfkey, unitized=False)
    area   = hf_areas[hfkey],
    vector = scale_vector(normal, drawing_scale)
    sp     = formdiagram.vertex_coordinates(ckey)
    ep     = add_vectors(sp, vector)
    color  = hf_c_dict[hfkey]
    lines.append({
        'start': sp,
        'end'  : ep,
        'color': color,
        'arrow': 'end',
        'name' : '{}.edge.loads.{}.{}'.format(formdiagram.name, hfkey, area)})

# 5. draw force diagram --------------------------------------------------------
forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=forcediagram.halffaces_on_boundary(), color=hf_c_dict)

# 5. draw form diagram --------------------------------------------------------
formdiagram.draw()
compas_rhino.draw_lines(lines,
                        layer=formdiagram.layer,
                        clear=False,
                        redraw=False)
