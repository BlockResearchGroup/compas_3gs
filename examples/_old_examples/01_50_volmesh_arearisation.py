from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.utilities import i_to_blue

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_rhino.objects import VolMeshObject

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.rhino import VolMeshSelector
from compas_3gs.rhino import VolmeshConduit

from compas_3gs.utilities import compare_initial_current
from compas_3gs.utilities import volmesh_face_areaness

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
# 2. select faces and assign target areas
# ------------------------------------------------------------------------------
rs.EnableRedraw(True)

hfkeys = VolMeshSelector.select_halffaces(forcediagram, message="Select faces to resize.")

# area_dict = {fkey: forcediagram.halfface_oriented_area(fkey) for fkey in hfkeys}
# avg = sum(area_dict.values()) / len(area_dict)

target_area = rs.GetReal("Enter target area for the chosen halffaces", minimum=0, maximum=1000.0)

target_areas = {}
for hfkey in hfkeys:
    target_areas[hfkey] = target_area


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------
forcediagram.clear()

initial_areaness = volmesh_face_areaness(forcediagram, target_areas)

# conduit
conduit = VolmeshConduit(forcediagram)


def callback(forcediagram, k, args, refreshrate=10):
    if k % refreshrate:
        return
    current_areaness = volmesh_face_areaness(forcediagram, target_areas)
    face_colordict = compare_initial_current(current_areaness,
                                             initial_areaness,
                                             color_scheme=i_to_blue)
    conduit.face_colordict = face_colordict
    conduit.redraw()


# planarise
with conduit.enabled():
    volmesh_planarise(forcediagram,
                      kmax=1000,
                      target_areas=target_areas,
                      fix_all_normals=True,
                      tolerance_area=0.01,
                      callback=callback,
                      print_result_info=True)


# update / redraw
forcediagram.draw()
