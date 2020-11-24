from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

import scriptcontext as sc

import compas_rhino

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.utilities import get_force_mags
from compas_3gs.utilities import get_force_colors_uv
from compas_3gs.utilities import get_force_colors_hf

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__commandname__ = "TGS_unified_diagram"


def RunCommand(is_interactive):

    if '3GS' not in sc.sticky:
        compas_rhino.display_message('3GS has not been initialised yet.')
        return

    scene = sc.sticky['3GS']['scene']

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('force')
    if not objects:
        compas_rhino.display_message("There is no force.diagram in the scene.")
        return
    force = objects[0]

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('form')
    if not objects:
        compas_rhino.display_message("There is no form.diagram in the scene.")
        return
    form = objects[0]


    # unified diagram ----------------------------------------------------------

    while True:

        rs.EnableRedraw(True)

        alpha = rs.GetReal('unified diagram scale', minimum=0.01, maximum=1.0)

        if alpha is None:
            break

        if not alpha:
            break

        # 1. get colors ----------------------------------------------------------------
        hf_color = (0, 0, 0)

        uv_c_dict = get_force_colors_uv(force.diagram, form.diagram, gradient=True)
        hf_c_dict = get_force_colors_hf(force.diagram, form.diagram, uv_c_dict=uv_c_dict)

        # 2. compute unified diagram geometries ----------------------------------------
        halffaces, prism_faces = volmesh_ud(force.diagram, form.diagram, scale=alpha)

        # 3. halffaces and prisms ------------------------------------------------------
        faces = []
        face_colors = {}
        for hfkey in force.diagram.halffaces():
            vkeys = force.diagram.halfface_vertices(hfkey)
            hf_xyz = [halffaces[hfkey][i] for i in vkeys]
            name = '{}.face.ud.{}'.format(force.diagram.name, hfkey)
            faces.append({'points': hf_xyz,
                          'name': name,
                          'color': hf_color})

        forces = get_force_mags(force.diagram, form.diagram)

        for uv in prism_faces:
            name = '{}.face.ud.prism.{}'.format(force.diagram.name, uv)

            for face in prism_faces[uv]:
                faces.append({'points': face,
                              'name': name,
                              'color': uv_c_dict[uv]})

        # 4. draw ----------------------------------------------------------------------
        force.diagram.clear()
        form.diagram.clear()

        form.diagram.draw_edges(color=uv_c_dict)

        compas_rhino.draw_faces(faces,
                                layer=force.diagram.layer,
                                clear=False,
                                redraw=False)







    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
