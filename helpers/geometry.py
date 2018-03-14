from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi

from compas.geometry import orient_points

from compas.geometry import angle_vectors
from compas.geometry import is_ccw_xy
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import angle_vectors
from compas.geometry import translate_points
from compas.geometry import rotate_points


# def orient_points(points, reference_plane=None, target_plane=None):
#     if not target_plane:
#         target_plane    = [(0., 0., 0.,), (0., 0., 1.)]
#     if not reference_plane:
#         reference_plane = [(0., 0., 0.,), (0., 0., 1.)]
#     vec_rot   = cross_vectors(reference_plane[1], target_plane[1])
#     angle     = angle_vectors(reference_plane[1], target_plane[1])
#     points    = rotate_points(points, vec_rot, angle, reference_plane[0])
#     vec_trans = subtract_vectors(target_plane[0], reference_plane[0])
#     points    = translate_points(points, vec_trans)
#     return points


def sort_points_ccw(points_dict, plane):

    xyz = {key: orient_points(points_dict[key], reference_plane=plane) for key in points_dict}

    keys = xyz.keys()

    if len(keys) == 1:
        ordered = keys
    else:
        ordered = [keys[0]]
        a = xyz[key]
        for i, nbr in enumerate(keys[1:]):
            c = xyz[nbr]
            pos = 0
            b = xyz[ordered[pos]]
            while not is_ccw_xy(a, b, c):
                pos += 1
                if pos > i:
                    break
                b = xyz[ordered[pos]]
            if pos == 0:
                pos = -1
                b = xyz[ordered[pos]]
                while is_ccw_xy(a, b, c):
                    pos -= 1
                    if pos < -len(ordered):
                        break
                    b = xyz[ordered[pos]]
                pos += 1
            ordered.insert(pos, nbr)

    return ordered
