from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_3gs.rhino import rhino_vertex_move


__commandname__ = "TGS_form_move_vertices"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('form')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    form = objects[0]

    # --------------------------------------------------------------------------

    vertices = form.select_vertices()

    rhino_vertex_move(form.diagram, vertices)

    form.diagram.update_angle_deviations()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
