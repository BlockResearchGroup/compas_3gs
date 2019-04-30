from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import centroid_points

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.algorithms.helpers import print_result


__all__ = ['volmesh_reciprocate']


def volmesh_reciprocate(volmesh,
                        formdiagram,
                        kmax=100,
                        weight=1.0,
                        fix_vkeys=[],
                        edge_min=None,
                        edge_max=None,
                        tolerance=0.001,
                        callback=None,
                        callback_args=None):
    """Perpendicularizes the faces of the polyhedral force diagram to the corresponding dual edges in the polyhedral form diagram.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object representing a polyhedral force diagram.
    formdiagram : VolMesh or Network
        A network object representing a polyhedral form diagram.
    kmax : int, optional [100]
        Maximum number of iterations.
    weight : float, optional [1.0]
        A float, between 0 and 1, which determines how much each diagram changes. 1 changes the form diagram only, while 0 changes the force diagram only. Default is ``1.0``.
    fix_vkeys : list, optional []
        List of vkeys to fix.
    edge_min : float, optional [None]
        Value for minimum edge length to be imposed.
    edge_max : float, optional [None]
        Value for maximum edge length allowed.
    tolerance: float, optional [0.001]
        Value for convergence tolerance. Deviation is measured by the the dot product of the input and target vectors.
    callback : callable, optional [None]
        A user-defined callback function to be executed after every iteration.
    callback_args : tuple, optional [None]
        Additional parameters to be passed to the callback.

    Raises
    ------
    Exception
        If a callback is provided, but it is not callable.

    Notes
    -----
        The orientations of the boundary faces of the polyhedral force diagram are always fixed by default.

    .. seealso ::
        compas.geometry.network_parallelise_edges

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
        target_vectors[(u, v)]  = {'fkey'  : u_hfkey,
                                   'target': target}
        target_normals[u_hfkey] = target

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------
    for k in range(kmax):

        # ----------------------------------------------------------------------
        #   3. update form diagram
        # ----------------------------------------------------------------------
        if weight != 0:

            new_form_xyz = {vkey: [] for vkey in formdiagram.vertex}

            for u, v in target_vectors:
                target_v = target_vectors[(u, v)]['target']
                edge_v   = formdiagram.edge_vector(u, v, unitized=False)

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

                # check edge orientation ---------------------------------------
                direction = _get_lambda(edge_v, target_v)
                l *= direction

                # collect new coordinates --------------------------------------
                if u in free_vkeys:
                    new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_v, -1 * l))
                    new_form_xyz[u].append(new_u_xyz)

                if v in free_vkeys:
                    new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_v, l))
                    new_form_xyz[v].append(new_v_xyz)

            # compute new vertex coordinates -----------------------------------
            for vkey in free_vkeys:
                final_xyz = centroid_points(new_form_xyz[vkey])
                formdiagram.vertex_update_xyz(vkey, final_xyz)

        # ----------------------------------------------------------------------
        #   4. update force diagram
        # ----------------------------------------------------------------------
        if weight != 1:
            volmesh_planarise(volmesh,
                              kmax=1,
                              target_normals=target_normals,
                              fix_boundary_normals=True)

        # ----------------------------------------------------------------------
        #   5. check convergence
        # ----------------------------------------------------------------------
        deviation = _check_deviation(volmesh, formdiagram)

        if deviation < tolerance:
            print_result('Reciprocation', k, deviation)
            break

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(volmesh, formdiagram, k, callback_args)


def cellnetwork_reciprocate(cellnetwork):
    raise NotImplementedError


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
    deviation = 0
    for u, v in network.edges():
        u_hf, v_hf = volmesh.cell_pair_hfkeys(u, v)
        normal = volmesh.halfface_normal(u_hf)
        edge   = network.edge_vector(u, v, unitized=True)
        dot    = dot_vectors(normal, edge)
        perp_check = 1 - abs(dot)
        if perp_check > deviation:
            deviation = perp_check
    return deviation


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
