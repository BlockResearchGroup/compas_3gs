from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from copy import deepcopy

from compas_rhino.helpers.volmesh import volmesh_select_faces
from compas_rhino.helpers import mesh_from_surface
from compas_rhino.selectors import VertexSelector

from compas_rhino.helpers import mesh_select_faces

from compas_3gs.rhino import VolmeshHalffaceInspector
from compas_3gs.rhino.control import set_target_areas

from compas_3gs.diagrams import Cell

from compas_3gs.rhino import rhino_volmesh_from_polysurfaces


from compas_3gs.rhino import rhino_mesh_planarise

from compas_3gs.rhino import rhino_volmesh_planarise


try:
    import Rhino
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# 1. select rhino polysurfaces
guid = rs.GetObject("select polysurface", filter=rs.filter.polysurface)
rs.HideObjects(guid)

cell = mesh_from_surface(Cell, guid)

cell.draw()
cell.draw_facelabels()
rs.EnableRedraw(True)


# 2. set target areas
target_areas = {2: 5,
                4: 5,
                9: 5}

avg_fkeys = [fkey for fkey in cell.face if fkey not in target_areas]


print(avg_fkeys)
print(target_areas)


# 3. initial face normals as targets
target_normals = {fkey: cell.face_normal(fkey) for fkey in cell.face}


rhino_mesh_planarise(cell,
                     kmax=3,

                     target_normals=target_normals,
                     target_areas=target_areas,

                     avg_fkeys=avg_fkeys,

                     refreshrate=1)

cell.draw()
