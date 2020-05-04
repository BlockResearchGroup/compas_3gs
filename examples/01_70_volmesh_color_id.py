from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas_rhino.geometry import RhinoSurface

from compas_3gs.diagrams import FormNetwork, ForceVolMesh
from compas_3gs.algorithms import volmesh_dual_network, volmesh_reciprocate
from compas_3gs.utilities import get_index_colordict, get_force_colors_hf
from compas_3gs.datastructures import VolMesh3gsArtist, Network3gsArtist

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

rs.HideObjects(guids)


# ------------------------------------------------------------------------------
# 2. make dual network from volmesh (form diagram)
# ------------------------------------------------------------------------------

# construct the dual_network (form diagram) from volmesh (force diagram)
form_layer = 'form_network'
formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer

# transform dual_network in x-direction
x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move

formdiagramartist = Network3gsArtist(formdiagram, layer=form_layer)

# ------------------------------------------------------------------------------
# 3. reciprocate
# ------------------------------------------------------------------------------

volmesh_reciprocate(forcediagram,
                    formdiagram,
                    kmax=1000,
                    weight=1,
                    edge_min=0.5,
                    edge_max=20,
                    tolerance=0.01)


# ------------------------------------------------------------------------------
# 4. visualisation - color id
# ------------------------------------------------------------------------------

uv_c_dict = get_index_colordict(list(formdiagram.edges()))
hf_c_dict = get_force_colors_hf(forcediagram, formdiagram, uv_c_dict=uv_c_dict)

faces_to_draw = [fkey for fkey in forcediagram.faces() if fkey in forcediagram.halffaces_interior()]

forcediagramartist.clear()
forcediagramartist.draw_edges()
forcediagramartist.draw_faces(keys=faces_to_draw, color=hf_c_dict)

formdiagramartist.clear()
formdiagramartist.draw_edges(color=uv_c_dict)
