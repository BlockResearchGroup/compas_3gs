from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "TGS_settings"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # settings here ...

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
