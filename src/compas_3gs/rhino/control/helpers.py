from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from copy import deepcopy

try:
    import rhinoscriptsyntax as rs
    import Rhino
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['get_initial_point',
           'get_target_point',

           'set_target_areas']


def get_initial_point(message='Point to move from?'):
    ip = Rhino.Input.Custom.GetPoint()
    ip.SetCommandPrompt(message)
    ip.Get()
    ip = ip.Point()
    return ip


def get_target_point(constraint, OnDynamicDraw, option='None', message='Point to move to?'):
    gp = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt(message)
    if option == 'None':
        gp.Constrain(constraint)
    if option != 'None':
        gp.Constrain(constraint, option)
    gp.DynamicDraw += OnDynamicDraw
    gp.Get()
    gp = gp.Point()
    return gp


def set_target_areas(area_dict):

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
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
