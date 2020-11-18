from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import dot_vectors

from compas.utilities import i_to_rgb
from compas.utilities import i_to_blue
from compas.utilities import i_to_green
from compas.utilities import i_to_red

from compas_3gs.utilities.topology import pair_uv_to_hf


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['get_index_colordict',
           'valuedict_to_colordict',
           'compare_initial_current',

           'get_force_mags',
           'get_force_colors_uv',
           'get_force_colors_hf',

           'print_result']


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
    """Convert a list of keys to a dictionary of key-color pairs based on a color gradient scheme.

    Parameters
    ----------
    key_list : list
        List of keys.
    color_scheme
        Desired color gradient scheme (i.e. i_to_rgb, i_to_red, i_to_blue, etc.)

    Returns
    -------
    c_dict : dict
        Dictionary of key-color pairs, from lowest to highest based on a color gradient scheme.

    """
    c_dict = {}

    if key_list:

        for index, key in enumerate(key_list):

            if len(key_list) == 1:
                value = 1
            else:
                value = float(index) / (len(key_list) - 1)

            color = color_scheme(value)
            c_dict[key] = color

    return c_dict


def valuedict_to_colordict(value_dict, color_scheme=i_to_rgb):
    """Convert a dictionary of key-value pairs to a dictionary of key-color pairs.

    Parameters
    ----------
    value_dict : dict
        Dictionary of key-value pairs.
    color_scheme
        Desired color gradient scheme (i.e. i_to_rgb, i_to_red, i_to_blue, etc.)

    Returns
    -------
    c_dict : dict
        Dictionary of key-color pairs, from lowest to highest based on a color gradient scheme.

    """
    c_dict = {}

    lb = min(value_dict.values())
    ub = max(value_dict.values())

    for key in value_dict:

        value = (value_dict[key] - lb) / (ub - lb)
        color = color_scheme(value)
        c_dict[key] = color

    return c_dict


def compare_initial_current(current_value_dict,
                            initial_value_dict,
                            color_scheme=i_to_rgb):
    """

    """
    color_dict = {}

    for key in current_value_dict:

        current = current_value_dict[key]
        initial = initial_value_dict[key]

        if current > 0.01:

            if initial < 0.01:
                value = 0
            else:
                value = current / initial

            color_dict[key] = color_scheme(value)

    return color_dict


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   force related
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def get_force_mags(volmesh, network):
    """Returns a dictionary of (u,v)-magnitude pairs.
    Negative magnitude means compression, while positive magnitude means tension.
    """
    uv_hf_dict = pair_uv_to_hf(network, volmesh)

    mags = {}

    for u, v in network.edges():
        hfkey = uv_hf_dict[(u, v)]
        edge_vector = network.edge_vector(u, v)
        face_normal = volmesh.halfface_normal(hfkey)
        face_area = volmesh.halfface_area(hfkey)
        dot = dot_vectors(face_normal, edge_vector)

        if dot < 0:
            factor = -1

        if dot > 0:
            factor = 1

        force = face_area * factor

        mags[(u, v)] = force

    return mags


def get_force_colors_uv(volmesh,
                        network,
                        gradient=False,
                        tol=0.001):
    """Returns a dictionary of (u,v)-color pairs.
    Blue means compression, and red means tension.
    """
    c_dict = {}
    f_dict = get_force_mags(volmesh, network)
    f_range = sorted(f_dict.values())

    c_forces = [x for x in f_range if x < 0]
    t_forces = [x for x in f_range if x > 0]

    for edge in f_dict:
        force = f_dict[edge]

        if force < 0:  # if compression
            color = (0, 0, 255)
            if gradient:
                min_c = abs(c_forces[-1])
                max_c = abs(c_forces[0])
                color = i_to_blue((abs(force) - min_c) / (max_c - min_c))

        if force > 0:  # if tension
            color = (255, 0, 0)
            if gradient:
                min_t = t_forces[0]
                max_t = t_forces[-1]
                color = i_to_red((force - min_t) / (max_t - min_t))

        if force == 0 or force < tol:  # if close to zero
            color = (255, 255, 255)

        c_dict[edge] = color

    return c_dict


def get_force_colors_hf(volmesh,
                        network,
                        uv_c_dict=None,
                        gradient=False,
                        boundary=False,
                        tol=0.001):
    """Returns a dictionary of hfkey-color pairs.
    """
    uv_hf_dict = pair_uv_to_hf(network, volmesh)

    uv_c_dict = uv_c_dict or get_force_colors_uv(volmesh,
                                                 network,
                                                 gradient=gradient)

    # interior halffaces -------------------------------------------------------
    hf_c_dict = {}
    for uv in uv_c_dict:
        u_hfkey = uv_hf_dict[uv]
        v_hfkey = volmesh.halfface_opposite_halfface(u_hfkey)

        hf_c_dict[u_hfkey] = uv_c_dict[uv]
        hf_c_dict[v_hfkey] = uv_c_dict[uv]

    # boundary halffaces -------------------------------------------------------
    if boundary:
        b_hfkeys = volmesh.halffaces_on_boundaries()
        b_hf_areas = {hfkey: volmesh.halfface_area(hfkey) for hfkey in b_hfkeys}
        b_hf_c_dict = valuedict_to_colordict(b_hf_areas,
                                             color_scheme=i_to_green)
        for hfkey in b_hfkeys:
            hf_color = (0, 255, 0)

            if gradient:
                hf_color = b_hf_c_dict[hfkey]
            hf_c_dict[hfkey] = hf_color

    return hf_c_dict


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   other
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def print_result(name, k, deviation):
    """Prints the result of an algorithm.

    Parameters
    ----------
    name : string
        name of the algorithm
    k : int
        number of iterations
    deviation : float
        deviation

    """
    name = str(name)

    print('===================================================================')
    print('')
    print(name, 'ended after', k, 'iterations.')
    print('')
    print('Max deviation :', deviation)
    print('')
    print('===================================================================')


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
