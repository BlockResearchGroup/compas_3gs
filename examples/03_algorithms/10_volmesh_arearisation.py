from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from copy import deepcopy

from compas_rhino.helpers.volmesh import volmesh_select_faces
from compas_rhino.selectors import VertexSelector

from compas_3gs_rhino.control import VolmeshHalffaceInspector

from compas_3gs_rhino.wrappers import rhino_volmesh_from_polysurfaces
from compas_3gs_rhino.wrappers import rhino_volmesh_planarise

try:
    import Rhino
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _set_target_areas(area_dict):

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt("Enter target areas")

    # face key -----------------------------------------------------------------
    sortedkeys  = sorted(area_dict.keys())
    key_strings = [str("key_" + str(key)) for key in sortedkeys]
    fkey_index  = 0
    key_list    = go.AddOptionList("pick_face", ["All"] + key_strings, fkey_index)

    # assign new target areas --------------------------------------------------
    new_area_dict = deepcopy(area_dict)

    while True:

        opt = go.Get()

        if go.CommandResult() != Rhino.Commands.Result.Success:
            break

        elif opt == Rhino.Input.GetResult.Option:  # keep picking options
            if go.OptionIndex() == key_list:
                fkey_index = int(go.Option().CurrentListOptionIndex)

                if fkey_index == 0:
                    avg = sum(area_dict.values()) / len(area_dict)

                    target_area = rs.GetReal("Enter target area for ALL faces", avg, 0, 1000.0)
                    if target_area:
                        for key in new_area_dict:
                            new_area_dict[key] = target_area

                else:
                    fkey_key = sortedkeys[fkey_index - 1]
                    current_area = area_dict[fkey_key]
                    target_area = rs.GetReal("Enter target area value", current_area, 0, 1000.0)
                    if target_area:
                        new_area_dict[fkey_key] = target_area

            # print current targets --------------------------------------------
            print('-----------------------------------------------------------')
            for fkey in new_area_dict:
                print("face", fkey, "has target area of :", new_area_dict[fkey])
            print('-----------------------------------------------------------')

            continue

        break

    return new_area_dict


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   example
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
forcediagram = rhino_volmesh_from_polysurfaces()


# ------------------------------------------------------------------------------
# 2. select faces and assign target areas
# ------------------------------------------------------------------------------
hfkeys = volmesh_select_faces(forcediagram)

forcediagram.clear()
forcediagram.draw_edges()
forcediagram.draw_faces(keys=hfkeys)
forcediagram.draw_face_labels(text={hfkey: str(hfkey) for hfkey in hfkeys})
rs.EnableRedraw(True)

# ------------------------------------------------------------------------------
# 3. Enter target area
# ------------------------------------------------------------------------------
current_area_dict = {fkey: forcediagram.halfface_oriented_area(fkey) for fkey in hfkeys}
target_areas      = _set_target_areas(current_area_dict)


# ------------------------------------------------------------------------------
# 4. arearise
# ------------------------------------------------------------------------------
rhino_volmesh_planarise(forcediagram,
                        kmax=1000,

                        target_areas=target_areas,

                        fix_boundary_normals=True,
                        fix_all_normals=False,
                        area_tolerance=0.001,

                        refreshrate=10)
