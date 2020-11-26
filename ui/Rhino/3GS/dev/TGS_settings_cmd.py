from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_3gs.rhino import SettingsForm
from compas_3gs.rhino import ForceVolMeshObject
from compas_3gs.rhino import FormNetworkObject


__commandname__ = "TGS_settings"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    SettingsForm.from_scene(scene, object_types=[ForceVolMeshObject, FormNetworkObject], global_settings=['3GS', 'Solvers'])

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
