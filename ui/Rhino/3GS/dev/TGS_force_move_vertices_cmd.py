from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_3gs.rhino import rhino_vertex_move


__commandname__ = "TGS_force_move_vertices"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('force')
    if not objects:
        compas_rhino.display_message("There is no force diagram in the scene.")
        return
    force = objects[0]

    # --------------------------------------------------------------------------

    vertices = force.select_vertices()

    rhino_vertex_move(force.diagram, vertices)

    objects = scene.find_by_name('form')
    if not objects:
        force.check_eq()
        scene.update()
        return
    form = objects[0]

    form.diagram.update_angle_deviations()

    force.check_eq()
    form.check_eq()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
