from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.rhino import rhino_vertex_move
from compas_3gs.rhino import rhino_vertex_align
from compas_3gs.rhino import rhino_vertex_modify_fixity
from compas_3gs.rhino import rhino_volmesh_vertex_lift

from compas_3gs.rhino import draw_vertex_fixities

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
forcediagram = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer_force
forcediagram.attributes['name'] = layer_force

forcediagram.draw()

# ------------------------------------------------------------------------------
# 2. modify volmesh vertices
# ------------------------------------------------------------------------------

while True:

    rs.EnableRedraw(True)

    modify = rs.GetString('modify volmesh vertices', strings=[
                          'move', 'align', 'lift', 'fixity', 'exit'])

    if modify is None or modify == 'exit':
        rs.EnableRedraw(False)
        break

    if modify == 'move':
        rhino_vertex_move(forcediagram)

    elif modify == 'align':
        rhino_vertex_align(forcediagram)

    elif modify == 'lift':
        rhino_volmesh_vertex_lift(forcediagram)

    elif modify == 'fixity':
        rhino_vertex_modify_fixity(forcediagram)

    forcediagram.draw()
    draw_vertex_fixities(forcediagram)
