from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import draw_corresponding_elements
from compas_3gs.rhino import draw_network_pipes
from compas_3gs.rhino import draw_compression_tension
from compas_3gs.rhino import draw_network_external_forces
from compas_3gs.rhino import draw_network_internal_forces

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

forcediagram.draw(layer=layer)


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------
layer = 'form_network'

formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = layer
formdiagram.attributes['name'] = layer

x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move

volmesh_reciprocate(forcediagram,
                    formdiagram,
                    kmax=1000,
                    weight=1,
                    edge_min=0.5,
                    edge_max=20,
                    tolerance=0.01)

formdiagram.draw(layer=layer)

# ------------------------------------------------------------------------------
# 3. visualisation types
# ------------------------------------------------------------------------------

while True:

    display = rs.GetString('pick visualisation type',
                           strings=['id',
                                    'compression_tension',
                                    'pipes',
                                    'external_forces',
                                    'internal_forces',
                                    'exit'])

    rs.EnableRedraw(True)

    if display is None or display == 'exit':
        break

    if display == 'id':
        formdiagram.clear()
        draw_corresponding_elements(forcediagram, formdiagram)

    elif display == 'pipes':
        scale = rs.GetReal('scale', 1, 0.01, 10.0)
        formdiagram.clear()
        draw_network_pipes(forcediagram, formdiagram, scale=scale)

    elif display == 'compression_tension':
        forcediagram.clear()
        formdiagram.clear()
        draw_compression_tension(forcediagram, formdiagram, gradient=True)

    elif display == 'external_forces':
        scale = rs.GetReal('scale', 1, 0.01, 10.0)
        formdiagram.draw()
        draw_network_external_forces(forcediagram, formdiagram, gradient=True, scale=scale)

    elif display == 'internal_forces':
        scale = rs.GetReal('scale', 1, 0.01, 10.0)
        formdiagram.clear()
        draw_network_internal_forces(forcediagram, formdiagram, scale=scale)

    rs.EnableRedraw(True)

rs.EnableRedraw(False)
forcediagram.draw()
formdiagram.draw()
