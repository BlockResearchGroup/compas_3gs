from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces

from compas_rhino import unload_modules
unload_modules('compas')

from compas_3gs.diagrams import FormNetwork, ForceVolMesh
from compas_3gs.algorithms import volmesh_dual_network, volmesh_reciprocate
from compas_3gs.rhino import ReciprocationConduit

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

# select Rhino polysurfaces
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

# construct the volmesh (force diagram) from Rhino polysurfaces
force_layer = 'force_volmesh'
forcediagram       = ForceVolMesh()
forcediagram       = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = force_layer
forcediagram.attributes['name'] = force_layer

# visualise the force_volmesh
forcediagram.draw(layer=force_layer)


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------

# construct the dual network (form diagram) from volmesh (force diagram)
form_layer = 'form_network'
formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer

# transform dual_network and visualise it
x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move
formdiagram.draw(layer=form_layer)


# ------------------------------------------------------------------------------
# 3. get reciprocation weight factor
# ------------------------------------------------------------------------------

# input weight factor to control how much the form and force diagrams are chaning
# relatively to each other during the form-finding procedure
weight = rs.GetReal(
    "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)


# ------------------------------------------------------------------------------
# 4. reciprocate
# ------------------------------------------------------------------------------

# clear the original force and form diagrams
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
                        tolerance=0.01,
                        callback=callback,
                        print_result_info=True)

# update / redraw the force and form diagrams
forcediagram.draw()
formdiagram.draw()
