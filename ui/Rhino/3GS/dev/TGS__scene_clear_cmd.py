from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "TGS__scene_clear"


def RunCommand(is_interactive):

    scene = sc.sticky['3GS']['scene']
    if not scene:
        return

    options = ["Yes", "No"]
    option = compas_rhino.rs.GetString("Clear all 3GS objects?", strings=options, defaultString="No")
    if not option:
        return

    if option == "Yes":
        scene.clear_layers()
        scene.purge()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
