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
from compas_rhino.utilities import xdraw_cylinders

from compas_3gs.utilities import pair_hf_to_uv
from compas_3gs.utilities import pair_uv_to_hf

from compas_3gs_rhino.display.helpers import get_index_colordict
from compas_3gs_rhino.display.helpers import valuedict_to_colordict
from compas_3gs_rhino.display.helpers import get_force_mags
from compas_3gs_rhino.display.helpers import get_force_colors_uv
from compas_3gs_rhino.display.helpers import get_force_colors_hf


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'display_mode_colors',
    'display_mode_ct',
    'display_mode_pipes',
    'display_mode_vectors'
]


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   display modes
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************










# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   display modes
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************



def display_mode_colors(volmesh, network, label=False):

    hf_uv_dict = pair_hf_to_uv(volmesh, network)
    uv_c_dict  = get_index_colordict(list(network.edges()))
    hf_c_dict  = get_force_colors_hf(volmesh, network, uv_c_dict=uv_c_dict)
    hfkeys     = hf_uv_dict.keys()

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(keys=hfkeys, color=hf_c_dict)

    network.clear()
    network.draw_edges(color=uv_c_dict)

    if label:
        text_dict = {fkey: str(fkey) for fkey in hfkeys}
        volmesh.draw_face_labels(text=text_dict, color=hf_c_dict)
        network.draw_edge_labels(color=uv_c_dict)


def display_mode_ct(volmesh, network, gradient=False, label=False):

    uv_c_dict = get_force_colors_uv(volmesh, network, gradient=gradient)
    hf_c_dict = get_force_colors_hf(volmesh, network, uv_c_dict=uv_c_dict)

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(keys=hf_c_dict.keys(), color=hf_c_dict)

    network.clear()
    network.draw_edges(color=uv_c_dict)


def display_mode_pipes(volmesh, network, colors=True, gradient=False, scale=1):

    uv_c_dict  = get_force_colors_uv(volmesh, network, gradient=gradient)
    hf_c_dict  = get_force_colors_hf(volmesh, network, uv_c_dict=uv_c_dict)
    uv_hf_dict = pair_uv_to_hf(volmesh, network)
    cylinders  = []
    for uv in network.edges():
        color = uv_c_dict[uv]
        if not colors:
            color = (0, 0, 0)
        cylinders.append({
            'start': network.vertex_coordinates(uv[0]),
            'end'  : network.vertex_coordinates(uv[1]),
            'radius': volmesh.halfface_area(uv_hf_dict[uv]) * scale,
            'color': color,
            'layer': network.layer})

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(keys=hf_c_dict.keys(), color=hf_c_dict)

    network.clear()
    network.draw_edges(color=uv_c_dict)

    xdraw_cylinders(cylinders, cap=True)


def display_mode_vectors(volmesh, network, vkeys=None, gradient=False, scale=1):

    if not vkeys:
        vkeys = network.vertex.keys()

    uv_c_dict = get_force_colors_uv(volmesh, network, gradient=gradient)
    hf_c_dict = get_force_colors_hf(volmesh, network, uv_c_dict=uv_c_dict)
    uv_f_dict = get_force_mags(volmesh, network)

    arrows = []
    for u in vkeys:
        nbr_vkeys = network.vertex_neighbors(u)

        for v in nbr_vkeys:
            uv = (u, v)
            if uv not in uv_f_dict:
                uv = (v, u)
            force = uv_f_dict[uv]

            vector = network.edge_direction(u, v)
            u_xyz = network.vertex_coordinates(u)
            v_xyz = add_vectors(u_xyz, scale_vector(vector, abs(force) * scale))

            sp = u_xyz
            ep = v_xyz

            if force < 0 :  # if compression
                sp = v_xyz
                ep = u_xyz

            arrows.append({
                'start': sp,
                'end'  : ep,
                'color': uv_c_dict[uv],
                'arrow': 'end',
                'layer': network.layer,
                'name' : '{}.edge.{}'.format(network.name, uv)})

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(keys=hf_c_dict.keys(), color=hf_c_dict)

    network.clear()
    xdraw_lines(arrows)



def display_mode_unified_diagram(volmesh, network):
    pass
