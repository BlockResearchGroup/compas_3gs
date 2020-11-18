from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.rhino import VertexSelector

from compas.utilities import i_to_red

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.rhino import VolmeshConduit

from compas_3gs.utilities import compare_initial_current
from compas_3gs.utilities import volmesh_face_flatness

# from compas_3gs.rhino import bake_cells_as_polysurfaces

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram = ForceVolMesh()
forcediagram = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer

forcediagram.draw()


# ------------------------------------------------------------------------------
# 2. pick vertices to fix
# ------------------------------------------------------------------------------
rs.EnableRedraw(True)

vkeys = VertexSelector.select_vertices(forcediagram,
                                       message='Select vertices to fix:')


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------
forcediagram.clear()

initial_flatness = volmesh_face_flatness(forcediagram)

# conduit
conduit = VolmeshConduit(forcediagram)


def callback(forcediagram, k, args, refreshrate=10):
    if k % refreshrate:
        current_flatness = volmesh_face_flatness(forcediagram)
        face_colordict = compare_initial_current(current_flatness,
                                                 initial_flatness,
                                                 color_scheme=i_to_red)
        conduit.face_colordict = face_colordict
        conduit.redraw()


# planarise
with conduit.enabled():
    volmesh_planarise(forcediagram,
                      kmax=500,
                      fix_vkeys=vkeys,
                      fix_boundary_normals=False,
                      tolerance_flat=0.05,
                      callback=callback,
                      print_result_info=True)

# update / redraw
forcediagram.draw()

# bake_cells_as_polysurfaces(forcediagram)
