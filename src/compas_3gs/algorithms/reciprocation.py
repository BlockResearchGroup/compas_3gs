from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import centroid_points
from compas.geometry import project_points_plane
from compas.geometry import distance_point_point

from compas_3gs.algorithms import volmesh_planarise


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['volmesh_reciprocate']


def volmesh_reciprocate(volmesh,
                        formdiagram,
                        kmax=100,
                        weight=1,
                        fix_vkeys=[],
                        edge_min=None,
                        edge_max=None,
                        tolerance=0.001,
                        callback=None,
                        callback_args=None,
                        print_result=False):
    """Perpendicularizes the polyhedral form and force diagrams.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.
    formdiagram : VolMesh or Network
        The dual network or volmesh object.
    kmax : int, optional [100]
        Maximum number of iterations.
    weight : float, optional [1]
        A float, between 0 and 1.
        Determines how much each diagram changes.
        weight = 1 means only the form diagram is updated.
        wegith = 0.5 means both diagrams are updated.
        weight = 0 means only the force diagram is updated.
    tolerance: float, optional [0.001]
        Sets the convergence tolerance.
    callback : callable, optional [None]
        A user-defined callback function to be executed after every iteration.
    callback_args : tuple, optional [None]
        Additional parameters to be passed to the callback.

    Raises
    ------
    Exception
        If a callback is provided, but it is not callable.

    """

    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    free_vkeys = list(set(formdiagram.vertex) - set(fix_vkeys))

    # --------------------------------------------------------------------------
    #   1. compute target vectors
    # --------------------------------------------------------------------------
    target_vectors = {}
    target_normals = {}
    for u, v in formdiagram.edges():
        u_hfkey     = volmesh.cell_pair_hfkeys(u, v)[0]
        face_normal = scale_vector(volmesh.halfface_normal(u_hfkey), weight)
        edge_vector = scale_vector(formdiagram.edge_vector(u, v), 1 - weight)
        target      = normalize_vector(add_vectors(face_normal, edge_vector))
        target_vectors[(u, v)] = {'fkey'  : u_hfkey,
                                  'target': target}
        target_normals[u_hfkey] = target

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------

    for k in range(kmax):

        # ----------------------------------------------------------------------
        #   form diagram
        # ----------------------------------------------------------------------
        if weight != 0:

            form_deviation = 0
            new_form_xyz   = {vkey: [] for vkey in formdiagram.vertex}

            for u, v in target_vectors:
                hfkey    = target_vectors[(u, v)]['fkey']
                target_v = target_vectors[(u, v)]['target']
                face_n   = volmesh.halfface_normal(hfkey)
                edge_v   = formdiagram.edge_vector(u, v, unitized=False)

                # check edge orientation ---------------------------------------
                direction = _get_lambda(edge_v, target_v)

                # check deviation ----------------------------------------------
                dot = dot_vectors(face_n, normalize_vector(edge_v))
                perp_check = abs(1 - abs(dot))
                if perp_check > form_deviation:
                    form_deviation = perp_check

                # target edge length -------------------------------------------
                l = length_vector(edge_v)

                # min edge
                l_min = formdiagram.edge[u][v]['l_min']
                if edge_min:
                    l_min = edge_min
                if l < l_min:
                    l = l_min

                # max edge
                l_max = formdiagram.edge[u][v]['l_max']
                if edge_max:
                    l_max = edge_max
                if l > l_max:
                    l = l_max

                l *= direction

                # compute new coordinates --------------------------------------
                if u in free_vkeys:
                    new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_v, -1 * l))
                    new_form_xyz[u].append(new_u_xyz)

                if v in free_vkeys:
                    new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_v, l))
                    new_form_xyz[v].append(new_v_xyz)

            # compute new coordinates ------------------------------------------
            for vkey in free_vkeys:
                final_xyz = centroid_points(new_form_xyz[vkey])
                formdiagram.vertex_update_xyz(vkey, final_xyz)

            # Check convergence ------------------------------------------------
            if form_deviation < tolerance:
                break

        # ----------------------------------------------------------------------
        #   form diagram
        # ----------------------------------------------------------------------
        if weight != 1:
            volmesh_planarise(volmesh,
                              kmax=1,
                              target_normals=target_normals)

        # ----------------------------------------------------------------------
        #   callback
        # ----------------------------------------------------------------------
        if callback:
            callback(volmesh, formdiagram, k, callback_args)

    if print_result:
        print('==============================================================')
        print('')
        print('Reciprocation stopped after', k, 'iterations ...')
        print('... with max_deviation of :', form_deviation)
        print('')
        print('==============================================================')


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   reciprocation helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _get_lambda(vector_1, vector_2):
    dot = dot_vectors(vector_1, vector_2)
    if dot < 0:
        return -1
    else:
        return 1


def _check_deviation(volmesh, network):
    pass


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



















    # # ==========================================================================
    # #   loop
    # # ==========================================================================

    # lines = []
    # polylines = []

    # iteration = 1

    # for k in range(kmax):



    #     deviation = 0

    #     relative_change = 0


    #     # ======================================================================
    #     #   FORCE DIAGRAM
    #     # ======================================================================
    #     # volmesh_planarise_faces(volmesh,
    #     #                         count=1,
    #     #                         target_normals=target_normals,
    #     #                         conduit=False)

    #     # ======================================================================
    #     #   FORM DIAGRAM
    #     # ======================================================================
    #     new_formdiagram_xyz = {vkey: [] for vkey in formdiagram.vertex}

    #     for hfkey in halfface_uv:

    #         u, v           = halfface_uv[hfkey]
    #         current_normal = volmesh.halfface_normal(hfkey)
    #         target_normal  = target_normals[hfkey]

    #         #   compute lambda : checking orientations -------------------------
    #         edge_vector = formdiagram.edge_vector(u, v, unitized=False)
    #         dot_v       = dot_vectors(normalize_vector(edge_vector), target_normal)
    #         if dot_v < 0:
    #             target_normal = scale_vector(target_normal, -1)

    #         #   check perpendicularity status ----------------------------------
    #         perp_check = abs(1 - abs(dot_v))

    #         if perp_check > deviation:
    #             deviation = perp_check

    #         #   target edge length -----------------------------------------
    #         dist = length_vector(edge_vector)
    #         if dist < min_edge:
    #             dist = min_edge
    #         if dist > max_edge:
    #             dist = max_edge

    #         direction = _get_lambda(current_normal, edge_vector)
    #         dist *= direction

    #         #   compute and add new xyz for v ------------------------------
    #         new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_normal, -1 * dist))
    #         new_formdiagram_xyz[u].append(new_u_xyz)
    #         new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_normal, dist))
    #         new_formdiagram_xyz[v].append(new_v_xyz)

    #     # ======================================================================
    #     #   UPDATE
    #     # ======================================================================
    #     for vkey in new_formdiagram_xyz:
    #         if vkey not in fix_vkeys:
    #             if new_formdiagram_xyz[vkey]:
    #                 initial_xyz = formdiagram.vertex_coordinates(vkey)
    #                 final_xyz = centroid_points(new_formdiagram_xyz[vkey])
    #                 formdiagram.vertex_update_xyz(vkey, final_xyz)

    #                 iteration_change = distance_point_point(initial_xyz, final_xyz)
    #                 if iteration_change > relative_change:
    #                     relative_change = iteration_change

    #     # ======================================================================
    #     #   DRAWING
    #     # ======================================================================

    #     # for u, v in formdiagram.edges_iter():
    #     #     lines.append({'start' : formdiagram.vertex_coordinates(u),
    #     #                   'end'   : formdiagram.vertex_coordinates(v),
    #     #                   'layer' : form_layer})

    #     # ======================================================================
    #     #   EVALUATE
    #     # ======================================================================
    #     if deviation < tolerance:
    #         break


    #     sc.doc.Views.Redraw()
    #     count     -= 1
    #     iteration += 1

    # # ==========================================================================
    # #   END
    # # ==========================================================================


    # print('reciprocation ended at:', iteration)
    # print('deviation:', deviation)





# def _OLD_volmesh_reciprocate(volmesh,
#                              formdiagram,
#                              weight=1,
#                              count=500,
#                              min_edge=5,
#                              max_edge=50,
#                              tolerance=0.001):
#     """Perpendicularizes the polyhedral form and force diagrams.

#     Parameters
#     ----------
#     volmesh : VolMesh
#         A mesh object.
#     formdiagram : VolMesh or Network
#         The type of the dual mesh.
#         Defaults to the type of the provided mesh object.
#     weight : float
#         A float, between 0 and 1.
#         Determines how much each diagram changes.
#         Default is 1, where only the form diagram changes.
#         Value of 0 would change the force diagram only.
#     min_edge : float
#         Minimum length constraint for the form diagram edges.
#     max_edge : float
#         Maximum length constraint for the form diagram edges.
#     tolerance: float
#         Sets the convergence tolerance.

#     Returns
#     -------
#     perpendicularized volmesh and formdiagram.

#     """

#     # ==========================================================================
#     #   compute target vectors
#     # ==========================================================================
#     target_normals = {}
#     halfface_uv    = {}
#     #   for internal halffaces -------------------------------------------------
#     for u, v in formdiagram.edges_iter():
#         u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
#         face_normal   = scale_vector(volmesh.halfface_normal(u_hfkey), weight)
#         edge_vector   = scale_vector(formdiagram.edge_vector(u, v), 1 - weight)
#         target_vector = add_vectors(face_normal, edge_vector)
#         target_normals[u_hfkey] = normalize_vector(target_vector)
#         halfface_uv[u_hfkey]    = (u, v)
#     for hfkey in volmesh.halffaces_on_boundary():
#         target_normals[hfkey] = volmesh.halfface_normal(hfkey)

#     # ==========================================================================
#     #   conduit
#     # ==========================================================================
#     conduit = reciprocation_conduit(volmesh, formdiagram)
#     conduit.Enabled  = True

#     # ==========================================================================
#     #   loop
#     # ==========================================================================
#     iteration = 0

#     while count:

#         deviation = 0

#         new_volmesh_xyz     = {vkey: [] for vkey in volmesh.vertex}
#         new_formdiagram_xyz = {vkey: [] for vkey in formdiagram.vertex}

#         for hfkey in target_normals:

#             target_normal = target_normals[hfkey]

#             # ==================================================================
#             #   FOCE DIAGRAM
#             # ==================================================================

#             dot_v = dot_vectors(volmesh.halfface_normal(hfkey), target_normal)
#             perp_check = abs(1 - abs(dot_v))
#             if perp_check > deviation:
#                 deviation = perp_check

#             plane    = (volmesh.halfface_center(hfkey), target_normal)
#             for vkey in volmesh.halfface_vertices(hfkey):
#                 xyz     = volmesh.vertex_coordinates(vkey)
#                 new_xyz = project_point_plane(xyz, plane)
#                 new_volmesh_xyz[vkey].append(new_xyz)

#             # ==================================================================
#             #   FORM DIAGRAM
#             # ==================================================================
#             if hfkey in halfface_uv:
#                 u, v = halfface_uv[hfkey]
#                 #   checking orientations --------------------------------------
#                 edge_vector = formdiagram.edge_vector(u, v, unitized=False)
#                 dot_v       = dot_vectors(normalize_vector(edge_vector), target_normal)
#                 if dot_v < 0:
#                     target_normal = scale_vector(target_normal, -1)
#                 #   check perpendicularity status ------------------------------
#                 perp_check = abs(1 - abs(dot_v))
#                 if perp_check > deviation:
#                     deviation = perp_check
#                 #   target edge length -----------------------------------------
#                 dist = length_vector(edge_vector)
#                 if dist < min_edge:
#                     dist = min_edge
#                 if dist > max_edge:
#                     dist = max_edge
#                 #   compute and add new xyz for v ------------------------------
#                 new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_normal, -1 * dist))
#                 new_formdiagram_xyz[u].append(new_u_xyz)
#                 new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_normal, dist))
#                 new_formdiagram_xyz[v].append(new_v_xyz)

#         # ======================================================================
#         #   UPDATE
#         # ======================================================================
#         for vkey in new_volmesh_xyz:
#             if new_volmesh_xyz[vkey]:
#                 final_xyz = centroid_points(new_volmesh_xyz[vkey])
#                 volmesh.vertex_update_xyz(vkey, final_xyz)
#         for vkey in new_formdiagram_xyz:
#             if new_formdiagram_xyz[vkey]:
#                 final_xyz = centroid_points(new_formdiagram_xyz[vkey])
#                 formdiagram.vertex_update_xyz(vkey, final_xyz)

#         # ======================================================================
#         #   EVALUATE
#         # ======================================================================
#         if deviation < tolerance:
#             break
#         sc.doc.Views.Redraw()
#         count     -= 1
#         iteration += 1

#     # ==========================================================================
#     #   END
#     # ==========================================================================
#     conduit.Enabled = False
#     del conduit

#     print('reciprocation ended at:', iteration)
#     print('deviation:', deviation)

#     volmesh.draw()
#     formdiagram.draw()

