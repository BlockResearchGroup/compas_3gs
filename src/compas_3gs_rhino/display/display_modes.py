from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.utilities import i_to_rgb
from compas.utilities import i_to_green
from compas.utilities import i_to_red
from compas.utilities import i_to_blue

from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point
from compas.geometry import centroid_points
from compas.geometry import project_points_plane
from compas.geometry import bestfit_plane
from compas.geometry import scale_vector
from compas.geometry import add_vectors

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_points
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_faces

from compas_3gs_rhino.display.helpers import get_index_colordict
from compas_3gs_rhino.display.helpers import get_value_colordict

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['draw_volmesh_boundary_forces']


# ==============================================================================
#   display modes
# ==============================================================================

def draw_volmesh_colors(volmesh, network):
    pass


def draw_volmesh_pipes(volmesh, network):
    pass


def draw_volmesh_vectors(volmesh, network):
    pass


def draw_volmesh_boundary_forces(volmesh, network, show_value=False, scale=1.0):

    volmesh.clear()
    network.clear()

    hfkeys    = volmesh.halffaces_on_boundary()
    hf_areas  = {hfkey: volmesh.halfface_area(hfkey) for hfkey in hfkeys}
    hf_colors = get_value_colordict(hf_areas)

    lines = []
    dots  = []

    for hfkey in hfkeys:
        ckey   = volmesh.halfface_cell(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        vector = scale_vector(normal, scale)
        sp     = network.vertex_coordinates(ckey)
        ep     = add_vectors(sp, vector)

        lines.append({
            'start': ep,
            'end'  : sp,
            'color': hf_colors[hfkey],
            'arrow': 'end',
            'name' : '{}.edge.boundary_force.{}'.format(network.name, hfkey)})

        if show_value:
            dots.append({
                'pos'  : midpoint_point_point(sp, ep),
                'text' : str(round(hf_areas[hfkey], 3)),
                'name' : '{}.edge.boundary.{}'.format(network.name, hfkey),
                'color': hf_colors[hfkey]})



    network.draw()
    xdraw_lines(lines, layer=network.layer, clear=False, redraw=False)
    xdraw_labels(dots, layer=network.layer, clear=False, redraw=False)

    volmesh.draw_edges()
    volmesh.draw_faces(color=hf_colors)

    return


def draw_volmesh_unified_diagram(volmesh, network):
    pass


# ==============================================================================
#   helpers
# ==============================================================================
