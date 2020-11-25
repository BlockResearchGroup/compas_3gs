from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

import scriptcontext as sc

import compas_rhino

from compas_3gs.algorithms import volmesh_ud

from compas_3gs.utilities import get_force_colors_uv

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
        compas_rhino.display_message("There is no force diagram in the scene.")
        return
    force = objects[0]

    # get ForceVolMeshObject from scene
    objects = scene.find_by_name('form')
    if not objects:
        compas_rhino.display_message("There is no form diagram in the scene.")
        return
    form = objects[0]

    # check global constraints -------------------------------------------------

    force.check_eq()
    form.check_eq()

    if not force.settings['_is.valid'] or not form.settings['_is.valid']:
        options = ["Yes", "No"]
        option = compas_rhino.rs.GetString("System is not in equilibrium... proceed?", strings=options, defaultString="No")
        if not option:
            return
        if option == "No":
            return

    show_loads = form.settings['show.loads']
    form.settings['show.loads'] = False

    # unified diagram ----------------------------------------------------------
    while True:

        rs.EnableRedraw(True)

        alpha = rs.GetReal('unified diagram scale', minimum=0.01, maximum=1.0)

        if alpha is None:
            break

        if not alpha:
            break

        compas_rhino.clear_layer(force.layer)
        compas_rhino.clear_layer(form.layer)

        # 1. get colors --------------------------------------------------------
        hf_color = (0, 0, 0)

        uv_c_dict = get_force_colors_uv(force.diagram, form.diagram, gradient=True)

        # 2. compute unified diagram geometries --------------------------------
        cells, prisms = volmesh_ud(force.diagram, form.diagram, scale=alpha)

        # 3. draw --------------------------------------------------------------
        for cell in cells:
            vertices = cells[cell]['vertices']
            faces = cells[cell]['faces']
            compas_rhino.draw_mesh(vertices, faces, layer=force.layer, name=str(cell), color=hf_color, redraw=False)

        for edge in prisms:
            vertices = prisms[edge]['vertices']
            faces = prisms[edge]['faces']
            compas_rhino.draw_mesh(vertices, faces, layer=force.layer, name=str(edge), color=uv_c_dict[edge], redraw=False)

        form.artist.draw_edges(color=uv_c_dict)

    form.settings['show.loads'] = show_loads

    scene.save()

# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':

    RunCommand(True)
