from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import scale_vector

from compas_3gs.algorithms.other import golden_section_search

from compas_3gs.operations import cell_split_indet_face_vertices
from compas_3gs.operations import cell_relocate_face


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['cell_arearise_face']


def cell_arearise_face(cell,
                       fkey,
                       target_area,

                       tol=1e-3,

                       callback=None,
                       callback_args=None):

    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    cell_split_indet_face_vertices(cell, fkey)

    area   = cell.face_area(fkey)
    normal = cell.face_normal(fkey)
    center = cell.face_centroid(fkey)

    # --------------------------------------------------------------------------
    #   get move direction
    # --------------------------------------------------------------------------
    sign = 1  # if it needs to get larger...
    if area - target_area > 0:
        sign = -1  # if it needs to be smaller...

    if area * target_area < 0 :  # if it needs to flip...
        sign = -1

    move_dir = _get_move_direction(cell, fkey) * sign

    # --------------------------------------------------------------------------
    #   evaluation function
    # --------------------------------------------------------------------------

    def evaluation(x):
        xyz      = add_vectors(center, scale_vector(normal, x * move_dir))
        new_area = _evaluate_new_face_area(cell, fkey, xyz, normal)

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(cell, callback_args)

        return abs(new_area - target_area)

    # --------------------------------------------------------------------------
    #   golden section search
    # --------------------------------------------------------------------------
    a = 0
    b = abs(area - target_area)

    z = golden_section_search(evaluation, a, b, tol=tol)

    # --------------------------------------------------------------------------
    #   update cell
    # --------------------------------------------------------------------------
    xyz = add_vectors(center, scale_vector(normal, z * move_dir))
    cell_relocate_face(cell, fkey, xyz, normal)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _get_move_direction(cell, fkey):

    normal     = cell.face_normal(fkey)
    center     = cell.face_center(fkey)
    area       = cell.face_area(fkey)

    new_center = add_vectors(center, normal)

    new_area   = _evaluate_new_face_area(cell, fkey, new_center)

    if new_area > area:
        move_dir = 1

    if new_area < area:
        move_dir = -1

    cell_relocate_face(cell, fkey, center, normal)

    if new_area == area:
        raise Exception('Pulling this face will not change its area!')

    return move_dir


def _evaluate_new_face_area(cell, fkey, xyz, init_normal=None):

    if not init_normal:
        init_normal = cell.face_normal(fkey)

    cell_relocate_face(cell, fkey, xyz, init_normal)

    new_area   = cell.face_area(fkey)
    new_normal = cell.face_normal(fkey)

    if dot_vectors(init_normal, new_normal) < 0:
        new_area *= -1

    return new_area


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
