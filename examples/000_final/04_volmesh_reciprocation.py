from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import ReciprocationConduit

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

forcediagram.draw(layer=layer)


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------
layer = 'form_network'

formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = layer
formdiagram.attributes['name'] = layer

x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.vertex:
    formdiagram.vertex[vkey]['x'] += x_move

formdiagram.draw(layer=layer)


# ------------------------------------------------------------------------------
# 3. get reciprocation weight factor
# ------------------------------------------------------------------------------
weight = rs.GetReal(
    "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)


# ------------------------------------------------------------------------------
# 4. reciprocate
# ------------------------------------------------------------------------------
forcediagram.clear()
formdiagram.clear()

# conduit
conduit = ReciprocationConduit(forcediagram, formdiagram)
def callback(forcediagram, formdiagram, k, args):
    if k % 2:
        conduit.redraw()

# reciprocation
with conduit.enabled():
    volmesh_reciprocate(forcediagram,
                        formdiagram,
                        kmax=1000,
                        weight=weight,
                        edge_min=0.5,
                        edge_max=20,
                        tolerance=0.001,
                        callback=callback)

# update / redraw
forcediagram.draw()
formdiagram.draw()
