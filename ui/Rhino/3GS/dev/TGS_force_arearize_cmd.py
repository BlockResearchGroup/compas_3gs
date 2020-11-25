from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas

from compas.utilities import i_to_red

import compas_rhino

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.rhino import VolmeshConduit

from compas_3gs.utilities import volmesh_face_areaness
from compas_3gs.utilities import compare_initial_current

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__commandname__ = "TGS_force_arearize"


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
    kmax = scene.settings['Solvers']['arearization.kmax']
    refresh = scene.settings['Solvers']['arearization.refreshrate']
    tol = scene.settings['Solvers']['arearization.tol']

    options = ['Iterations', 'Refreshrate', 'Set_target_areas', 'Fix_face_normals', 'Fix_vertices', 'Tolerance']

    # options ------------------------------------------------------------------
    fix_vertices = []
    target_areas = {}
    target_text = {}
    target_colors = {}
    target_normals = {}

    while True:

        rs.EnableRedraw(True)

        option = compas_rhino. rs.GetString('Press Enter to run or ESC to exit.', strings=options)

        if option is None:
            scene.clear_layers()
            scene.clear()
            scene.update()
            print("Arearization aborted!")
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

        elif option == 'Set_target_areas':

            while True:

                areas = {face: round(force.diagram.face_area(face), 2) for face in force.diagram.faces() if face not in target_areas}
                force.artist.draw_facelabels(text=areas)

                rs.EnableRedraw(True)

                faces = force.select_faces()

                if not faces or faces is None:
                    break

                target_area = rs.GetReal("Enter target area value", minimum=0.1, maximum=10000.0)

                if target_area:
                    for face in faces:

                        current_area = force.diagram.face_area(face)

                        if current_area > target_area:
                            color = (255, 0, 0)
                            text = str(round(current_area, 2)) + ' ---> ' + str(round(target_area, 2))
                        else:
                            color = (0, 0, 255)
                            text = str(round(current_area, 2)) + ' ---> ' + str(round(target_area, 2))

                        target_areas[face] = target_area
                        target_text[face] = text
                        target_colors[face] = color

                scene.clear_layers()
                scene.clear()
                scene.update()

                force.artist.draw_facelabels(text=target_text, color=target_colors)

        elif option == 'Fix_face_normals':
            target_normals = {}
            items = ("Boundary_faces", "No", "Yes"), ("Interior_Faces", "No", "Yes")
            boundary, interior = rs.GetBoolean("Fix normals of...", items, (False, False))
            if boundary:
                target_normals.update({face: force.diagram.face_normal(face) for face in force.diagram.halffaces_on_boundaries()})
            if interior:
                for face in force.diagram.faces():
                    if not force.diagram.is_halfface_on_boundary(face):
                        target_normals[face] = force.diagram.face_normal(face)

        elif option == 'Fix_vertices':
            fix_vertices += force.select_vertices()

        elif option == 'Tolerance':
            new_tol = compas_rhino.rs.GetReal('Enter areaness tolerance', tol, 0.001, 1.0)
            if new_tol or new_tol is not None:
                tol = new_tol

    if refresh > kmax:
        refresh = 0

    scene.settings['Solvers']['planarization.kmax'] = kmax
    scene.settings['Solvers']['planarization.refreshrate'] = refresh
    scene.settings['Solvers']['arearization.tol'] = tol

    # --------------------------------------------------------------------------
    # planarization
    # --------------------------------------------------------------------------

    if refresh > 0:

        initial_flatness = volmesh_face_areaness(force.diagram, target_areas)

        conduit = VolmeshConduit(force.diagram)

        def callback(forcediagram, k, args, refreshrate=refresh):
            if k % refreshrate:
                return
            current_flatness = volmesh_face_areaness(force.diagram, target_areas)
            face_colordict = compare_initial_current(current_flatness,
                                                     initial_flatness,
                                                     color_scheme=i_to_red)
            conduit.face_colordict = face_colordict
            conduit.redraw()

        # planarise
        with conduit.enabled():
            volmesh_planarise(force.diagram,
                              kmax=kmax,
                              target_areas=target_areas,
                              target_normals=target_normals,
                              fix_vkeys=fix_vertices,
                              fix_boundary_normals=False,
                              tolerance_flat=scene.settings['Solvers']['planarization.tol'],
                              tolerance_area=tol,
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
