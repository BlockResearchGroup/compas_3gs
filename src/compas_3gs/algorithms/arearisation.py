from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino as rhino

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry import distance_point_point
from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import centroid_points
from compas.geometry import midpoint_point_point
from compas.geometry import bestfit_plane
from compas.geometry import is_polygon_convex
from compas.geometry import project_points_plane

from compas.geometry.transformations.transformations import project_point_plane

from compas_rhino.helpers import volmesh_select_vertices

from compas.utilities import i_to_blue

# from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.operations import cell_collapse_short_edges

from compas_3gs.utilities import normal_polygon_general
from compas_3gs.utilities import area_polygon_general

from compas_3gs.utilities import scale_polygon


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['mesh_arearise']


def mesh_arearise(mesh,
                  kmax=100,
                  target_areas={},
                  target_normals={},
                  avg_fkeys=[],
                  area_tolerance=0.001,
                  callback=None,
                  callback_args=None):

    """

    complex faces are not allowed...

    footprint area is used instead of oriented area...


    """

    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    loops = []

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------
    for k in range(kmax):

        area_deviation = 0

        new_xyz = {vkey: [] for vkey in mesh.vertex}

        for fkey in mesh.face:

            f_vkeys  = mesh.face[fkey]
            f_pts    = [mesh.vertex_coordinates(vkey) for vkey in f_vkeys]
            f_center = centroid_points(f_pts)
            f_area   = mesh.face_area(fkey)
            # f_area   = _area_polygon_footprint(f_pts)

            target_area  = target_areas[fkey]

            delta = target_area - f_area

            # ------------------------------------------------------------------
            new_face = {vkey: mesh.vertex_coordinates(vkey) for vkey in f_vkeys}

            # ------------------------------------------------------------------
            #   project
            # ------------------------------------------------------------------
            if fkey in target_normals:
                target_plane = (f_center, target_normals[fkey])
                for vkey in f_vkeys:
                    xyz            = mesh.vertex_coordinates(vkey)
                    projected_xyz  = project_point_plane(xyz, target_plane)
                    new_face[vkey] = projected_xyz

            # ----------------------------------------------------------------
            #   for non-zero faces
            # ---------------------------------------------------------------
            if target_area != 0:
                scale = (target_area / f_area) ** 0.5


            # ------------------------------------------------------------------
            #   for zero faces
            # ------------------------------------------------------------------
            elif target_area == 0:
                scale = 1 - f_area * 0.1

                # if f_area < 1:
                #     scale = 1 - f_area
                # scale = 0.9

            new_face = scale_polygon(new_face, scale)

            # ==================================================================
            if target_area == 0:
                polyline = []
                for vkey in f_vkeys:
                    polyline.append(new_face[vkey])
                loops.append({'points': polyline + [polyline[0]],
                              'color' : i_to_blue(k / kmax),
                              'name'  : 'iteration-{0}.face-{1}'.format(k, fkey)})
            # ==================================================================

            areaness  = abs(f_area - target_area)
            if areaness > area_deviation:
                area_deviation = areaness

            # 6. collect new coordinates ---------------------------------------
            for vkey in new_face:
                new_xyz[vkey].append(new_face[vkey])



        # for u, v in mesh.edges():
        #     sp   = mesh.vertex_coordinates(u)
        #     ep   = mesh.vertex_coordinates(v)
        #     dist = distance_point_point(sp, ep)
        #     if dist < 0.5:
        #         mp = midpoint_point_point(sp, ep)
        #         new_xyz[u].append(mp)
        #         new_xyz[v].append(mp)



        # 7. compute new coordinates
        for vkey in mesh.vertex:
            final_xyz = centroid_points(new_xyz[vkey])
            mesh.vertex_update_xyz(vkey, final_xyz)


        # # 8. check convergence -------------------------------------------------
        cell_collapse_short_edges(mesh)


        # 8. check convergence -------------------------------------------------
        if area_deviation < area_tolerance:
            break

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(mesh, k, callback_args)

    # mesh.draw()

    rhino.xdraw_polylines(loops)

    print(area_deviation)
    print(k)



# volmesh_arearise = volmesh_planarise


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _area_polygon_footprint(points):

    area = 0
    p    = len(points)
    w    = centroid_points(points)

    for i in range(-1, len(points) - 1):
        u      = points[i]
        v      = points[i + 1]
        uv     = subtract_vectors(v, u)
        vw     = subtract_vectors(w, v)
        normal = scale_vector(cross_vectors(uv, vw), 0.5)
        area   += length_vector(normal)

    return area





# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# #
# #   arearise mesh
# #
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def mesh_arearise(mesh,
#                       count=100,
#                       target_normals=None,
#                       target_centers=None,
#                       target_areas={},
#                       fix_boundary=False,
#                       fix_all=False,
#                       omit_vkeys=[],
#                       flat_tolerance=0.0001,
#                       area_tolerance=0.0001):

#     # ..........................................................................

#     iteration = 0

#     while count:

#         flatness_deviation = 0
#         area_deviation     = 0
#         new_vertices       = {}

#         for hfkey in mesh.face:
#             hf_vkeys  = mesh.face[hfkey]
#             points    = [mesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
#             hf_normal = bestfit_plane(points)[1]
#             hf_area   = mesh.face_area(hfkey)
#             hf_center = mesh.face_center(hfkey)


#             if target_normals:
#                 if hfkey in target_normals:
#                     hf_normal = target_normals[hfkey]
#             if target_centers:
#                 if hfkey in target_centers:
#                     hf_center = target_centers[hfkey]

#             plane = (hf_center, hf_normal)


#             pt_dict = {}
#             for vkey in hf_vkeys:
#                 if vkey not in new_vertices:
#                     new_vertices[vkey] = []
#                 xyz           = mesh.vertex_coordinates(vkey)
#                 new_xyz       = project_point_plane(xyz, plane)
#                 pt_dict[vkey] = new_xyz
#                 dist          = distance_point_point(xyz, new_xyz)
#                 if dist > flatness_deviation:
#                     flatness_deviation = dist

#             if hfkey in target_areas:
#                 # if hf_area > 0.001:
#                 target_area = target_areas[hfkey]
#                 if target_area == 0:
#                     scale = 0.001
#                 else:
#                     scale       = (target_area / hf_area)**0.5
#                 pt_dict     = _scale_polygon(pt_dict, scale)
#                 difference  = abs(hf_area - target_area)
#                 if difference > area_tolerance:
#                     area_deviation = difference

#             for vkey in pt_dict:
#                 new_vertices[vkey].append(pt_dict[vkey])


#         # ----------------------------------------------------------------------
#         # compute new coordinates
#         # ----------------------------------------------------------------------
#         for vkey in new_vertices:
#             if vkey not in omit_vkeys:
#                 final_xyz = centroid_points(new_vertices[vkey])

#                 mesh.vertex[vkey]['x'] = final_xyz[0]
#                 mesh.vertex[vkey]['y'] = final_xyz[1]
#                 mesh.vertex[vkey]['z'] = final_xyz[2]

#         # ----------------------------------------------------------------------
#         # update
#         # ----------------------------------------------------------------------
#         if iteration > 1:
#             if flatness_deviation < flat_tolerance and area_deviation < area_tolerance:
#                 break

#         sc.doc.Views.Redraw()
#         iteration += 1
#         count -= 1

#     # ..........................................................................

#     print('===================================================================')
#     print('')
#     print('planarisation ended at:', iteration)
#     print('flatness deviation:', flatness_deviation)
#     print('area deviation:', area_deviation)
#     print('')
#     print('===================================================================')


# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# #
# #   helpers
# #
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def _get_current_normals(mesh):
#     normal_dict = {}
#     for hfkey in mesh.halfface:
#         center = mesh.halfface_center(hfkey)
#         normal = mesh.halfface_normal(hfkey)
#         normal_dict[hfkey] = {'normal': normal, 'center': center}
#     return normal_dict


# def _store_initial_normals(mesh):
#     for hfkey in mesh.halfface:
#         center = mesh.halfface_center(hfkey)
#         normal = mesh.halfface_normal(hfkey)
#         mesh.update_f_data(
#             hfkey,
#             attr_dict={'normal_i': normal, 'center_i': center})
#     return mesh


# def _scale_polygon(points_dict, scale):
#     points = points_dict.values()
#     center = centroid_points(points)
#     new_points_dict = {}
#     for key in points_dict:
#         point = points_dict[key]
#         vector = subtract_vectors(point, center)
#         new_point = add_vectors(center, scale_vector(vector, scale))
#         new_points_dict[key] = new_point
#     return new_points_dict
