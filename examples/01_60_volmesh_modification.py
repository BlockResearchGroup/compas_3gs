from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas_rhino.geometry import RhinoSurface

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.rhino import rhino_vertex_move, rhino_vertex_align, rhino_vertex_modify_fixity
from compas_3gs.rhino import rhino_volmesh_vertex_lift, draw_vertex_fixities
from compas_3gs.datastructures import VolMesh3gsArtist

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

# make a volmesh from polysurface
vertices = []
cells = []
for guid in guids:
    vertices_dict = {}
    polysurface= RhinoSurface.from_guid(guid) # this function doesn't work for extrusion objects
    mesh = polysurface.brep_to_compas()
    for key in mesh.vertices():
        if mesh.vertex_coordinates(key) not in vertices:
            vertices_dict[key] = len(vertices)
            vertices.append(mesh.vertex_coordinates(key))
        else:
            vertices_dict[key] = vertices.index(mesh.vertex_coordinates(key))
    cell = []
    for fkey in mesh.faces():
        face = [vertices_dict[vkey] for vkey in mesh.face_vertices(fkey)]
        cell.append(face)
    cells.append(cell)
    
forcediagram = ForceVolMesh.from_vertices_and_cells(vertices, cells)

force_layer = 'force_volmesh'
forcediagram.layer = force_layer
forcediagram.attributes['name'] = force_layer

# visualise the force_volmesh
forcediagramartist = VolMesh3gsArtist(forcediagram, layer=force_layer)
forcediagramartist.draw()

rs.HideObjects(guids)


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
        forcediagramartist.draw()
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
    forcediagramartist.clear()
    forcediagramartist.draw()

    draw_vertex_fixities(forcediagram, forcediagramartist)

    rs.EnableRedraw(True)

forcediagramartist.clear()
forcediagramartist.draw()
