from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas_rhino.geometry import RhinoSurface

from compas_3gs.diagrams import FormNetwork, ForceVolMesh
from compas_3gs.algorithms import volmesh_dual_network, volmesh_reciprocate
from compas_3gs.rhino import ReciprocationConduit
from compas_3gs.rhino import VolMesh3gsArtist, Network3gsArtist

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

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces
from compas.datastructures import VolMesh
forcediagram = volmesh_from_polysurfaces(ForceVolMesh, guids)

## make a volmesh from polysurface
#vertices = []
#cells = []
#for guid in guids:
#    vertices_dict = {}
#    polysurface= RhinoSurface.from_guid(guid) # this function doesn't work for extrusion objects
#    mesh = polysurface.brep_to_compas()
#    for key in mesh.vertices():
#        if mesh.vertex_coordinates(key) not in vertices:
#            vertices_dict[key] = len(vertices)
#            vertices.append(mesh.vertex_coordinates(key))
#        else:
#            vertices_dict[key] = vertices.index(mesh.vertex_coordinates(key))
#    cell = []
#    for fkey in mesh.faces():
#        face = [vertices_dict[vkey] for vkey in mesh.face_vertices(fkey)]
#        cell.append(face)
#    cells.append(cell)
    
#forcediagram = ForceVolMesh.from_vertices_and_cells(vertices, cells)

force_layer = 'force_volmesh'
forcediagram.layer = force_layer
forcediagram.attributes['name'] = force_layer

# visualise the force_volmesh
forcediagramartist = VolMesh3gsArtist(forcediagram, layer=force_layer)
forcediagramartist.draw()


# ------------------------------------------------------------------------------
# 2. make dual network (form diagram)
# ------------------------------------------------------------------------------

# construct the dual network (form diagram) from volmesh (force diagram)
form_layer = 'form_network'
formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer

print(formdiagram)

# transform dual_network and visualise it
x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move

formdiagramartist = Network3gsArtist(formdiagram, layer=form_layer)
formdiagramartist.draw_nodes()
formdiagramartist.draw_edges()


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
forcediagramartist.clear()
formdiagramartist.clear()

# conduit
conduit = ReciprocationConduit(forcediagram, formdiagram)




def callback(forcediagram, formdiagram, k, args):
    print(k)
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
forcediagramartist.draw()
formdiagramartist.draw_nodes()
formdiagramartist.draw_edges()
