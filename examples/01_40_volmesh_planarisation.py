from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas_rhino.geometry import RhinoSurface
from compas_rhino.objects.selectors import VertexSelector
from compas.utilities import i_to_red

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.algorithms import volmesh_planarise


from compas_3gs.rhino import VolmeshConduit, bake_cells_as_polysurfaces
from compas_3gs.utilities import compare_initial_current, volmesh_face_flatness
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
forcediagramartist.draw_vertices()   # PROBLEM: artist doesn't show up unitl the vertices are selected.
forcediagramartist.draw_vertexlabels()

rs.HideObjects(guids)

# ------------------------------------------------------------------------------
# 2. pick vertices to fix
# ------------------------------------------------------------------------------
vkeys = VertexSelector.select_vertices(forcediagram,
                                       message='Select vertices to fix:')


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------
# clear the original force diagram
forcediagramartist.clear()
# compute the initial face flatness of force volmesh
initial_flatness = volmesh_face_flatness(forcediagram)

# conduit
conduit = VolmeshConduit(forcediagram)


def callback(forcediagram, k, args):
    if k % 5:
        current_flatness = volmesh_face_flatness(forcediagram)
        face_colordict   = compare_initial_current(current_flatness,
                                                   initial_flatness,
                                                   color_scheme=i_to_red)
        conduit.face_colordict = face_colordict
        conduit.redraw()


# planarise
with conduit.enabled():
    volmesh_planarise(forcediagram,
                      kmax=1000,
                      fix_vkeys=vkeys,
                      fix_boundary_normals=False,
                      tolerance_flat=0.01,
                      callback=callback,
                      print_result_info=True)

# update / redraw
#forcediagram.draw()
bake_cells_as_polysurfaces(forcediagram)