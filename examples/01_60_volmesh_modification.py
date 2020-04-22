from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.rhino import rhino_vertex_move, rhino_vertex_align, rhino_vertex_modify_fixity
from compas_3gs.rhino import rhino_volmesh_vertex_lift, draw_vertex_fixities

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

# construct volmesh (force diagram) from Rhino polysurfaces
layer = 'force_volmesh'
forcediagram       = ForceVolMesh()
forcediagram       = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer
# visualise force_volmesh
forcediagram.draw(layer=layer)


# ------------------------------------------------------------------------------
# 2. modify volmesh vertices
# ------------------------------------------------------------------------------

while True:

    # choose vertices modification method 
    modify = rs.GetString('modify volmesh vertices', strings=[
                          'move', 'align', 'lift', 'fixity', 'exit'])
    rs.EnableRedraw(True)

    # invalid or no modification
    if modify is None or modify == 'exit':
        rs.EnableRedraw(False)
        forcediagram.draw()
        break

    # move the selected vertices
    if modify == 'move':
        rhino_vertex_move(forcediagram)
    # align the selected vertices
    elif modify == 'align':
        rhino_vertex_align(forcediagram)
    # duplicate and lift selected vertices
    elif modify == 'lift':
        rhino_volmesh_vertex_lift(forcediagram)
    # modify fixity of selected vertices
    elif modify == 'fixity':
        rhino_vertex_modify_fixity(forcediagram)
    
    # visualise the modified force_volmesh
    forcediagram.draw()
    draw_vertex_fixities(forcediagram)

    rs.EnableRedraw(True)

forcediagram.draw()
