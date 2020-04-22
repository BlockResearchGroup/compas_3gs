from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas.utilities import i_to_blue

from compas_rhino.geometry._constructors  import volmesh_from_polysurfaces
from compas_rhino.selectors import volmesh_select_faces

from compas_3gs.algorithms import volmesh_planarise
from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.rhino import VolmeshConduit
from compas_3gs.utilities import compare_initial_current
from compas_3gs.utilities import volmesh_face_areaness

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
# 2. select faces and assign target areas
# ------------------------------------------------------------------------------

# select the face to modify
hfkeys      = volmesh_select_faces(forcediagram)
# input target area value
area_dict   = {fkey: forcediagram.halfface_oriented_area(fkey) for fkey in hfkeys}
avg         = sum(area_dict.values()) / len(area_dict)
target_area = rs.GetReal("Enter target area for the chosen halffaces", avg, 0, 1000.0)
target_areas = {}
for hfkey in hfkeys:
    target_areas[hfkey] = target_area


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------

# clear the original force diagram
forcediagram.clear()
# compute the face areaness of force volmesh
initial_areaness = volmesh_face_areaness(forcediagram, target_areas)

# conduit
conduit = VolmeshConduit(forcediagram)


def callback(forcediagram, k, args):
    if k % 10:
        current_areaness = volmesh_face_areaness(forcediagram, target_areas)
        face_colordict   = compare_initial_current(current_areaness,
                                                   initial_areaness,
                                                   color_scheme=i_to_blue)
        conduit.face_colordict = face_colordict
        conduit.redraw()


# planarise
with conduit.enabled():
    volmesh_planarise(forcediagram,
                      kmax=5000,
                      target_areas=target_areas,
                      fix_all_normals=True,
                      tolerance_area=0.01,
                      callback=callback,
                      print_result_info=True)


# update / redraw
forcediagram.draw()
