from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_3gs.diagrams import FormNetwork

from compas.geometry import Translation

from compas_3gs.algorithms import volmesh_dual_network

from compas_3gs.rhino import relocate_formdiagram


__commandname__ = "TGS_primal"


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

    # make FormNetwork
    form = volmesh_dual_network(force.diagram, cls=FormNetwork)

    # set dual/primal
    form.dual = force.diagram
    force.diagram.primal = form

    # add FormNetworkObject
    translation = relocate_formdiagram(force.diagram, form)
    form.transform(Translation.from_vector(translation))
    form.update_angle_deviations()
    scene.add_formnetwork(form, name='form', layer='3GS::FormDiagram')

    # update
    scene.update()
    scene.save()

    print('Dual diagram successfully created.')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
