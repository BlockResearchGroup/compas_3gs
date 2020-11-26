from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces
from compas_rhino.objects.select import mesh_select_face

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.rhino import VolmeshHalffaceInspector
from compas_3gs.rhino import rhino_volmesh_pull_halffaces

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer_force = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram = ForceVolMesh()
forcediagram = volmesh_from_polysurfaces(forcediagram, guids, '2f')
forcediagram.layer = layer_force
forcediagram.attributes['name'] = layer_force

forcediagram.draw()


# --------------------------------------------------------------------------
#  1. display boundary halffaces
# --------------------------------------------------------------------------
boundary_halffaces = forcediagram.halffaces_on_boundaries()

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(faces=boundary_halffaces)

rs.EnableRedraw(True)

# --------------------------------------------------------------------------
#  2. select halfface and its dependents
# --------------------------------------------------------------------------
hf_inspector = VolmeshHalffaceInspector(forcediagram,
                                        dependents=True)
hf_inspector.enable()

hfkey = mesh_select_face(forcediagram)

hf_inspector.disable()

del hf_inspector


# ------------------------------------------------------------------------------
# 2. volmesh face pull
# ------------------------------------------------------------------------------

rhino_volmesh_pull_halffaces(forcediagram)
