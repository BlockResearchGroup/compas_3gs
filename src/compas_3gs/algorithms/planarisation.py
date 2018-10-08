from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import project_point_plane
from compas.geometry import bestfit_plane

from compas_rhino.helpers import volmesh_select_vertices

from compas_3gs_rhino.display import planarisation_conduit

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['volmesh_planarise_faces']


def volmesh_planarise_faces(volmesh,
                            count=100,
                            target_normals=None,
                            target_centers=None,
                            target_areas={},
                            fix_boundary=False,
                            fix_all=False,
                            omit_vkeys=[],
                            flat_tolerance=0.0001,
                            area_tolerance=0.0001):

    initial_normals = _get_current_normals(volmesh)
    boundary_hfkeys = set(volmesh.halffaces_on_boundary())

    special_vkeys = set()
    for hfkey in target_areas:
        special_vkeys.add(vkey for vkey in volmesh.halfface_vertices(hfkey))

    # ..........................................................................

    iteration = 0

    while count:

        flatness_deviation = 0
        area_deviation     = 0
        new_vertices       = {}

        for hfkey in volmesh.halfface:
            hf_vkeys  = volmesh.halfface_vertices(hfkey)
            points    = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            hf_normal = bestfit_plane(points)[1]
            hf_area   = volmesh.halfface_area(hfkey)
            hf_center = volmesh.halfface_center(hfkey)

            # ------------------------------------------------------------------
            # construct projection plane
            # ------------------------------------------------------------------
            if fix_all:
                hf_normal = initial_normals[hfkey]['normal']
            if target_normals:
                if hfkey in target_normals:
                    hf_normal = target_normals[hfkey]
            if target_centers:
                if hfkey in target_centers:
                    hf_center = target_centers[hfkey]
            if fix_boundary:
                if hfkey in boundary_hfkeys:
                    hf_normal = initial_normals[hfkey]['normal']
            plane = (hf_center, hf_normal)

            # project ----------------------------------------------------------
            pt_dict = {}
            for vkey in hf_vkeys:
                if vkey not in new_vertices:
                    new_vertices[vkey] = []
                xyz           = volmesh.vertex_coordinates(vkey)
                new_xyz       = project_point_plane(xyz, plane)
                pt_dict[vkey] = new_xyz
                dist          = distance_point_point(xyz, new_xyz)
                if dist > flatness_deviation:
                    flatness_deviation = dist
            # scale ------------------------------------------------------------
            if hfkey in target_areas:
                target_area = target_areas[hfkey]
                scale       = (target_area / hf_area)**0.5
                pt_dict     = _scale_polygon(pt_dict, scale)
                difference  = abs(hf_area - target_area)
                if difference > area_tolerance:
                    area_deviation = difference

            for vkey in pt_dict:
                if hfkey in target_areas:
                    new_vertices[vkey].append(pt_dict[vkey])
                else:
                    if vkey not in special_vkeys:
                        new_vertices[vkey].append(pt_dict[vkey])

        # ----------------------------------------------------------------------
        # compute new coordinates
        # ----------------------------------------------------------------------
        for vkey in new_vertices:
            if vkey not in omit_vkeys:
                final_xyz = centroid_points(new_vertices[vkey])
                volmesh.vertex_update_xyz(vkey, final_xyz)

        # ----------------------------------------------------------------------
        # update
        # ----------------------------------------------------------------------
        if iteration > 1:
            if flatness_deviation < flat_tolerance and area_deviation < area_tolerance:
                break

        sc.doc.Views.Redraw()
        iteration += 1
        count -= 1

    # ..........................................................................

    print('===================================================================')
    print('')
    print('planarisation ended at:', iteration)
    print('flatness deviation:', flatness_deviation)
    print('area deviation:', area_deviation)
    print('')
    print('===================================================================')


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _get_current_normals(volmesh):
    normal_dict = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        normal_dict[hfkey] = {'normal': normal, 'center': center}
    return normal_dict


def _store_initial_normals(volmesh):
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        volmesh.update_f_data(
            hfkey,
            attr_dict={'normal_i': normal, 'center_i': center})
    return volmesh


def _scale_polygon(points_dict, scale):
    points = points_dict.values()
    center = centroid_points(points)
    new_points_dict = {}
    for key in points_dict:
        point = points_dict[key]
        vector = subtract_vectors(point, center)
        new_point = add_vectors(center, scale_vector(vector, scale))
        new_points_dict[key] = new_point
    return new_points_dict
