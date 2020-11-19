from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


from compas_3gs.rhino import get_scene
import compas_rhino
from compas_3gs.rhino import tgs_undo


__commandname__ = "TGS_clear_all"


@tgs_undo
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    options = ["Yes", "No"]
    option = compas_rhino.rs.GetString("Clear all 3GS objects?", strings=options, defaultString="No")
    if not option:
        return

    if option == "Yes":
        scene.clear()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
