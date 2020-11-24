from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_rhino.objects.select import mesh_select_face

from compas_3gs.rhino import rhino_volmesh_pull_halffaces

from compas_3gs.rhino import VolmeshHalffaceInspector

__commandname__ = "TGS_force_pull_halffaces"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    # select halfface ----------------------------------------------------------
    boundary_halffaces = force.diagram.halffaces_on_boundaries()

    hf_inspector = VolmeshHalffaceInspector(
        force.diagram,
        hfkeys=boundary_halffaces,
        dependents=True)
    hf_inspector.enable()
    halfface = mesh_select_face(force.diagram)
    hf_inspector.disable()
    del hf_inspector

    # pull faces ---------------------------------------------------------------
    rhino_volmesh_pull_halffaces(force.diagram, hfkey=halfface)

    objects = scene.find_by_name('form')
    if not objects:
        scene.update()
        return
    form = objects[0]

    form.diagram.update_angle_deviations()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
