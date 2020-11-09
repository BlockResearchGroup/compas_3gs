from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import ReciprocationConduit

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_rhino.artists import NetworkArtist
from compas_rhino.artists import VolMeshArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()

rs.EnableRedraw(True)

# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer_force = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram = ForceVolMesh()
forcediagram = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer_force
forcediagram.attributes['name'] = layer_force

force_artist = VolMeshArtist(forcediagram, layer=layer_force)

force_artist.draw_faces()


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------
layer_form = 'form_network'

formdiagram = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = layer_form
formdiagram.attributes['name'] = layer_form

# move dual_network
offset = 2
width = formdiagram.bounding_box()[1][0] - formdiagram.bounding_box()[0][0]
for vkey in formdiagram.nodes():
    x = formdiagram.node_attribute(vkey, 'x')
    formdiagram.node_attribute(vkey, 'x', x + width * offset)

form_artist = NetworkArtist(formdiagram, layer=layer_form)

form_artist.draw_edges()


# ------------------------------------------------------------------------------
# 3. get reciprocation weight factor
# ------------------------------------------------------------------------------
weight = rs.GetReal(
    "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)


# ------------------------------------------------------------------------------
# 4. reciprocate
# ------------------------------------------------------------------------------

force_artist.clear_by_name()
form_artist.clear_by_name()


# conduit
conduit = ReciprocationConduit(forcediagram, formdiagram)


def callback(forcediagram, formdiagram, k, args):
    if k % 5:
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

# update / redraw
force_artist.draw_faces()
form_artist.draw_edges()
