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
from compas.geometry import project_point_plane
from compas.geometry import bestfit_plane
from compas.geometry import scale_vector
from compas.geometry import add_vectors

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_points
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_faces

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
           'get_value_colordict']


def get_index_colordict(key_list):
    color_dict = {}
    if key_list:
        for index, key in enumerate(key_list):
            if len(key_list) == 1:
                value = 1
            else:
                value  = float(index) / (len(key_list) - 1)
            color  = i_to_rgb(value)
            color_dict[key] = color
    return color_dict


def get_value_colordict(value_dict):
    color_dict = {}
    ub = max(value_dict.values())
    for key in value_dict:
        color = i_to_rgb(value_dict[key] / ub)
        color_dict[key] = color
    return color_dict
