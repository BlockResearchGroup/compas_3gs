from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules('compas')

from compas_rhino.geometry import RhinoSurface

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.rhino import draw_cell_labels
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
# 1. make volmesh from rhino polysurfaces
# ------------------------------------------------------------------------------
# select Rhino polysurfaces
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)

rs.HideObjects(guids)

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




# ------------------------------------------------------------------------------
# 2. visualise volmesh (force diagram)
# ------------------------------------------------------------------------------
# draw cells
layer = 'force_volmesh'
forceartist = VolMesh3gsArtist(forcediagram, layer=layer)
forceartist.draw()
forceartist.draw_vertexlabels()

# draw labels in the center of each cell
forcediagram.layer = layer
draw_cell_labels(forcediagram)
