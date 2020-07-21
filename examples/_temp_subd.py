from compas_rhino import unload_modules
unload_modules("compas")

import compas

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh


from compas_rhino.geometry import RhinoSurface
from compas_3gs.diagrams import Cell

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.rhino import draw_corresponding_elements
from compas_3gs.rhino import draw_network_pipes
from compas_3gs.rhino import draw_compression_tension
from compas_3gs.rhino import draw_network_external_forces
from compas_3gs.rhino import draw_network_internal_forces

from compas_3gs.rhino import Mesh3gsArtist, VolMesh3gsArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()



# select the polysurface which you create in Rhino
guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
# turn Rhino polysurface to a COMPAS single polyhedral cell
cell = RhinoSurface.from_guid(guid).brep_to_compas(cls=Cell())
rs.HideObjects(guid)

# draw the polyhedral cell
layer = 'cell'
cellartist = Mesh3gsArtist(cell, layer=layer)
cellartist.draw()
cellartist.redraw()

from compas_3gs.operations import check_cell_convexity
print(check_cell_convexity(cell))

print(cell)
#================== cell_cut_face_subdiv ==================
def rhino_cell_face_subdivide_barycentric(cell):
    from compas_rhino.objects.selectors import volmesh_select_face
    from compas_3gs.operations import cell_face_subdivide_barycentric
    fkey = volmesh_select_face(cell)
    volmesh = cell_face_subdivide_barycentric(cell, fkey)
    return volmesh

volmesh = rhino_cell_face_subdivide_barycentric(cell)


cellartist.clear()
cellsartist = VolMesh3gsArtist(volmesh, layer=layer)
cellsartist.draw_vertexlabels()
cellsartist.draw()
cellsartist.redraw()

print(list(volmesh.vertices()))
print(list(volmesh.cells()))
print(list(volmesh.cell_halffaces(0)))
print(list(volmesh.cell_halffaces(1)))
print(list(volmesh.cell_halffaces(2)))
print(list(volmesh.cell_halffaces(3)))