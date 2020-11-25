from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas.utilities import i_to_red

import compas_rhino

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.rhino import VolmeshConduit

from compas_3gs.utilities import volmesh_face_flatness
from compas_3gs.utilities import compare_initial_current


__commandname__ = "TGS_force_planarize"


def RunCommand(is_interactive):

    sc.doc.EndUndoRecord(sc.doc.CurrentUndoRecordSerialNumber)

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']
    if not scene:
        return

    # get ForceVolMeshObject from scene ----------------------------------------
    objects = scene.find_by_name('force')
    if not objects:
        compas_rhino.display_message("There is no force diagram in the scene.")
        return
    force = objects[0]

    # get global settings ------------------------------------------------------
    kmax = scene.settings['Solvers']['planarization.kmax']
    refresh = scene.settings['Solvers']['planarization.refreshrate']
    tol = scene.settings['Solvers']['planarization.tol']

    options = ['Iterations', 'Refreshrate', 'Fix_vertices', 'Tolerance']

    # options ------------------------------------------------------------------
    fix_vertices = []

    while True:
        option = compas_rhino. rs.GetString('Press Enter to run or ESC to exit.', strings=options)

        if option is None:
            print("Planarization aborted!")
            return

        if not option:
            break

        if option == 'Iterations':
            new_kmax = compas_rhino.rs.GetInteger('Enter number of iterations', kmax, 1, 10000)
            if new_kmax or new_kmax is not None:
                kmax = new_kmax

        elif option == 'RefreshRate':
            new_refresh = compas_rhino.rs.GetInteger('Refresh rate for dynamic visualisation', refresh, 0, 1000)
            if new_refresh or new_refresh is not None:
                refresh = new_refresh

        elif option == 'Fix_vertices':
            fix_vertices += force.select_vertices()

        elif option == 'Tolerance':
            new_tol = compas_rhino.rs.GetReal('Enter flatness tolerance', tol, 0.001, 1.0)
            if new_tol or new_tol is not None:
                tol = new_tol

    if refresh > kmax:
        refresh = 0

    scene.settings['Solvers']['planarization.kmax'] = kmax
    scene.settings['Solvers']['planarization.refreshrate'] = refresh
    scene.settings['Solvers']['planarization.tol'] = tol

    # --------------------------------------------------------------------------
    # planarization
    # --------------------------------------------------------------------------

    if refresh > 0:

        initial_flatness = volmesh_face_flatness(force.diagram)

        conduit = VolmeshConduit(force.diagram)

        def callback(forcediagram, k, args, refreshrate=refresh):
            if k % refreshrate:
                return
            current_flatness = volmesh_face_flatness(forcediagram)
            face_colordict = compare_initial_current(current_flatness,
                                                     initial_flatness,
                                                     color_scheme=i_to_red)
            conduit.face_colordict = face_colordict
            conduit.redraw()

        # planarise
        with conduit.enabled():
            volmesh_planarise(force.diagram,
                              kmax=kmax,
                              fix_vkeys=fix_vertices,
                              fix_boundary_normals=False,
                              tolerance_flat=tol,
                              callback=callback,
                              print_result_info=True)

    # check if there is form diagram -------------------------------------------
    objects = scene.find_by_name('form')
    if not objects:
        force.check_eq()
        scene.update()
        return
    form = objects[0]

    # update -------------------------------------------------------------------
    form.diagram.update_angle_deviations()

    form.check_eq()
    force.check_eq()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
