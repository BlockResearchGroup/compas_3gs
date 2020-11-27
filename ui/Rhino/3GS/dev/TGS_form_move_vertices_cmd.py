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
        compas_rhino.display_message("There is no form diagram in the scene.")
        return
    form = objects[0]

    # --------------------------------------------------------------------------

    current_setting = form.settings['show.nodes']
    if not current_setting:
        form.settings['show.nodes'] = True
        scene.update()

    vertices = form.select_vertices()

    rhino_vertex_move(form.diagram, vertices)

    form.settings['show.nodes'] = current_setting

    # --------------------------------------------------------------------------

    form.diagram.update_angle_deviations()

    objects = scene.find_by_name('force')
    if not objects:
        form.check_eq()
        scene.update()
        return
    force = objects[0]

    force.check_eq()
    form.check_eq()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
