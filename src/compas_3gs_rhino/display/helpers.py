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
from compas.geometry import dot_vectors

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_points
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_faces

from compas_3gs.utilities import pair_hf_to_uv


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['get_index_colordict',
           'valuedict_to_colordict',
           'get_force_colors_uv',
           'get_force_colors_hf']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   general
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def get_index_colordict(key_list, color_scheme=i_to_rgb):
    c_dict = {}
    if key_list:
        for index, key in enumerate(key_list):
            if len(key_list) == 1:
                value = 1
            else:
                value  = float(index) / (len(key_list) - 1)
            color  = color_scheme(value)
            c_dict[key] = color
    return c_dict


def valuedict_to_colordict(value_dict, color_scheme=i_to_rgb):
    """From value_dict to color_dict.
    """
    c_dict = {}
    ub = max(value_dict.values())
    for key in value_dict:
        value = value_dict[key] / ub
        color = color_scheme(value)
        c_dict[key] = color
    return c_dict


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   floor related
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def get_force_mags(volmesh, network):
    """Returns a dictionary of (u,v)-magnitude pairs.
    Negative magnitude means compression, while positive magnitude means tension.
    """
    mags = {}
    for u, v in network.edges():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        edge_vector      = network.edge_vector(u, v)
        face_normal      = volmesh.halfface_normal(u_hfkey)
        face_area        = volmesh.halfface_area(u_hfkey)
        dot              = dot_vectors(face_normal, edge_vector)
        if dot < 0:
            factor = -1
        if dot > 0:
            factor = 1
        force = face_area * factor
        mags[(u, v)] = force
        mags[(v, u)] = force
    return mags


def get_force_colors_uv(volmesh,
                        network,
                        gradient=False,
                        tol=0.001):
    """Returns a dictionary of (u,v)-color pairs.
    Blue means compression, and red means tension.
    """
    c_dict  = {}
    f_dict  = get_force_mags(volmesh, network)
    f_range = sorted(f_dict.values())
    max_c   = abs(f_range[0])  # max comrpession
    max_t   = f_range[-1]  # max tension
    for edge in f_dict:
        force = f_dict[edge]
        if force < 0:  # if compression
            color = (0, 0, 255)
            if gradient:
                color = i_to_blue(abs(force) / max_c)
        if force > 0:  # if tension
            color = (255, 0, 0)
            if gradient:
                color = i_to_red(force / max_t)
        if force == 0 or force < tol:  # if close to zero
            color = (255, 255, 255)
        c_dict[edge] = color
    return c_dict


def get_force_colors_hf(volmesh,
                        network,
                        uv_c_dict=None,
                        gradient=False,
                        tol=0.001):
    """Returns a dictionary of hfkey-color pairs.
    """
    hf_c_dict = {}
    if not uv_c_dict:
        uv_c_dict = get_force_colors_uv(volmesh,
                                        network,
                                        gradient=False,
                                        tol=0.001)
    hf_uv_dict = pair_hf_to_uv(volmesh, network)
    for hfkey in hf_uv_dict:
        uv = hf_uv_dict[hfkey]
        hf_c_dict[hfkey] = uv_c_dict[uv]
    return hf_c_dict





