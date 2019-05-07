from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import dot_vectors
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry.transformations.transformations import project_point_plane

from compas_3gs.utilities import scale_polygon

from compas_3gs.operations import cell_collapse_short_edges

from compas_3gs.utilities import print_result


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['mesh_planarise',
           'volmesh_planarise']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   mesh planarisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def mesh_planarise(mesh,
                   kmax=100,

                   target_centers={},
                   target_normals={},
                   target_areas={},

                   fix_vkeys=[],

                   avg_fkeys=[],

                   tolerance_flat=0.001,
                   tolerance_area=0.001,
                   tolerance_perp=0.001,

                   callback=None,
                   callback_args=None,

                   print_result_info=False):
    """Planarise the faces of a mesh.

    Planarisation of a mesh is implemented as a three-step iterative procedure.
    At every iteration, each face is first individually projected to its best-fit plane (unless a target normal is given).
    Then, each face is re-sized to its target area (if given).
    Finally, the new vertex coordinates are computed by taking the centroid of the disconnected corners of the faces.

    Parameters
    ----------

    mesh : Mesh
        A mesh object

    kmax : int, optional [100]
        Number of iterations.

    target_face_areas : dictionary, optional [{}]
        A dictionary of fkeys and target areas.
    target_face_normals : dictionary, optional [{}]
        A dictionary of fkeys and target face normals.
    target_face_centers : dictionary, optional [{}]
        A dictionary of fkeys and target face centers.

    omit_vkeys : list, optional [[]]
        List of vkeys to omit from arearisation.

    tolerance_flat: float, optional
        Convergence tolerance for face flatness.
    tolerance_area: float, optional
        Convergence tolerance for face areas.

    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.
    callback_args : tuple, optional
        Additional parameters to be passed to the callback.
        Default is ``None``.

    Raises
    ------
    Exception
        If a callback is provided, but it is not callable.

    .. seealso ::
        `compas.geometry.mesh_planarize_faces`

    """
    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    # --------------------------------------------------------------------------
    #   1. initialise
    # --------------------------------------------------------------------------
    free_vkeys = list(set(mesh.vertex) - set(fix_vkeys))

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------
    for k in range(kmax):

        deviation_flat = 0
        deviation_area = 0
        deviation_perp = 0

        new_xyz = {vkey: [] for vkey in mesh.vertex}

        # faces to be averaged -------------------------------------------------
        if avg_fkeys:
            avg_face_area = _avg_face_area(mesh, avg_fkeys)

        for fkey in mesh.face:

            # evaluate current face --------------------------------------------
            f_vkeys  = mesh.face_vertices(fkey)
            f_v_xyz  = mesh.face_coordinates(fkey)
            f_normal = mesh.face_normal(fkey)
            f_area   = mesh.face_area(fkey)
            f_center = centroid_points(mesh.face_coordinates(fkey))

            if fkey in target_centers:
                f_center = target_centers[fkey]

            if fkey in target_normals:
                target_normal = target_normals[fkey]

                # perpness deviation
                perpness = 1 - abs(dot_vectors(f_normal, target_normal))
                if perpness > deviation_perp:
                    deviation_perp = perpness

                f_normal = target_normal

            # projection plane -------------------------------------------------
            plane = (f_center, f_normal)

            # ------------------------------------------------------------------
            #   3. planarise
            # ------------------------------------------------------------------
            projected_face = []
            for xyz in f_v_xyz:
                projected_xyz = project_point_plane(xyz, plane)
                projected_face.append(projected_xyz)

                # planarisation deviation
                dist = distance_point_point(xyz, projected_xyz)
                if dist > deviation_flat:
                    deviation_flat = dist

            # ------------------------------------------------------------------
            #   4. arearise
            # ------------------------------------------------------------------
            if fkey in target_areas:
                target_area = target_areas[fkey]

            if fkey in avg_fkeys:
                target_area = avg_face_area

            # scale factor -----------------------------------------------------
            if target_area != 0:
                scale = (target_area / f_area) ** 0.5

            elif target_area == 0:
                scale = 1 - f_area * 0.1

            # scale ------------------------------------------------------------
            scaled_face = scale_polygon(projected_face, scale)

            # arearisation deviation
            areaness  = abs(f_area - target_area)
            if areaness > deviation_area:
                deviation_area = areaness

            # collect new coordinates
            for i in range(len(f_vkeys)):
                new_xyz[f_vkeys[i]].append(scaled_face[i])

        # ----------------------------------------------------------------------
        #   5. compute new volmesh vertex coordinates
        # ----------------------------------------------------------------------
        for vkey in free_vkeys:
            final_xyz = centroid_points(new_xyz[vkey])
            mesh.vertex_update_xyz(vkey, final_xyz)

        cell_collapse_short_edges(mesh)

        # ----------------------------------------------------------------------
        #   7. check convergence
        # ----------------------------------------------------------------------
        if deviation_flat < tolerance_flat and deviation_area < tolerance_area:

            if print_result_info:

                name      = "Mesh planarisation"
                deviation = deviation_flat

                if target_areas:
                    name      = "Mesh arearisation"
                    deviation = deviation_area

                print_result(name, k, deviation)

            break

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(mesh, k, callback_args)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh planarisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_planarise(volmesh,
                      kmax=100,

                      target_centers={},
                      target_normals={},
                      target_areas={},

                      fix_vkeys=[],

                      fix_boundary_normals=False,
                      fix_all_normals=False,

                      min_area=None,
                      max_area=None,

                      tolerance_flat=0.001,
                      tolerance_area=0.001,
                      tolerance_perp=0.001,

                      callback=None,
                      callback_args=None,

                      print_result_info=False):
    """Planarises the halffaces of a volmesh.

    Planarisation of a volmesh is implemented as a three-step iterative procedure.
    At every iteration, each halfface is first individually projected to its best-fit plane (unless a target normal is given).
    Then, each halfface is re-sized to its target area (if given).
    Finally, the new vertex coordinates are computed by taking the centroid of the disconnected corners of the halffaces.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.
    kmax : int, optional [100]
        Number of iterations.
    target_face_areas : dictionary, optional [{}]
        A dictionary of fkeys and target areas.
    target_face_normals : dictionary, optional [{}]
        A dictionary of fkeys and target face normals.
    target_face_centers : dictionary, optional [{}]
        A dictionary of fkeys and target face centers.
    omit_vkeys : list, optional [[]]
        List of vkeys to omit from arearisation.
    fix_boundary_face_normals : boolean, optional [False]
        Whether to keep the initial normals of the bondary faces.
    fix_all_face_normals : boolean, optional [False]
        Whether to keep the initial normals of all faces.
    tolerance_flat: float, optional
        Convergence tolerance for face flatness.
    tolerance_area: float, optional
        Convergence tolerance for face areas against target areas.
    tolerance_perp: float, optional
        Convergence tolerance for face perpendicularity against target normals.
    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.
    callback_args : tuple, optional
        Additional parameters to be passed to the callback.
        Default is ``None``.
    print_result_info : bool, optional
        If True, print the result of the algorithm.

    Raises
    ------
    Exception
        If a callback is provided, but it is not callable.

    .. seealso ::
        `compas.geometry.mesh_planarize_faces`

    """
    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    # --------------------------------------------------------------------------
    #   1. initialise
    # --------------------------------------------------------------------------
    free_vkeys      = list(set(volmesh.vertex) - set(fix_vkeys))
    initial_normals = _get_current_volmesh_normals(volmesh)
    boundary_fkeys  = volmesh.halffaces_on_boundary()

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------
    for k in range(kmax):

        deviation_flat = 0
        deviation_area = 0
        deviation_perp = 0

        new_xyz = {vkey: [] for vkey in volmesh.vertex}

        for fkey in volmesh.faces():

            fkey_pair = volmesh.halfface_opposite_halfface(fkey)

            # evaluate current face --------------------------------------------
            f_vkeys  = volmesh.halfface_vertices(fkey)
            f_v_xyz  = volmesh.halfface_coordinates(fkey)
            f_center = volmesh.halfface_center(fkey)
            f_normal = volmesh.halfface_oriented_normal(fkey)
            f_area   = volmesh.halfface_oriented_area(fkey)

            # override with manual target values -------------------------------
            if _pair_membership(fkey, fkey_pair, target_centers):
                f_center = target_centers[fkey]

            if _pair_membership(fkey, fkey_pair, target_normals):
                target_normal = target_normals[fkey]

                # perpness deviation
                perpness = 1 - abs(dot_vectors(f_normal, target_normal))
                if perpness > deviation_perp:
                    deviation_perp = perpness

                f_normal = target_normal

            if fix_boundary_normals:
                if fkey in boundary_fkeys:
                    f_normal = initial_normals[fkey]['normal']
            if fix_all_normals:
                f_normal = initial_normals[fkey]['normal']

            # projection plane -------------------------------------------------
            plane = (f_center, f_normal)

            # ------------------------------------------------------------------
            #   3. planarise
            # ------------------------------------------------------------------
            new_face = []
            for xyz in f_v_xyz:
                projected_xyz = project_point_plane(xyz, plane)
                new_face.append(projected_xyz)

                # planarisation deviation
                flatness = distance_point_point(xyz, projected_xyz)
                if flatness > deviation_flat:
                    deviation_flat = flatness

            # ------------------------------------------------------------------
            #   4. arearise
            # ------------------------------------------------------------------
            if fkey in target_areas:
                target_area = target_areas[fkey]
                scale       = (target_area / f_area) ** 0.5

                # scale
                new_face = scale_polygon(new_face, scale)

                # arearisation deviation
                areaness  = abs(f_area - target_area)
                if areaness > deviation_area:
                    deviation_area = areaness

            # collect new coordinates ------------------------------------------
            for i in range(len(f_vkeys)):
                new_xyz[f_vkeys[i]].append(new_face[i])

        # ----------------------------------------------------------------------
        #   5. compute new volmesh vertex coordinates
        # ----------------------------------------------------------------------
        for vkey in free_vkeys:
            final_xyz = centroid_points(new_xyz[vkey])
            volmesh.vertex_update_xyz(vkey, final_xyz)

        # ----------------------------------------------------------------------
        #   6. check convergence
        # ----------------------------------------------------------------------
        if deviation_flat < tolerance_flat and deviation_area < tolerance_area and deviation_perp < tolerance_perp:

            if print_result_info:

                name      = "Volmesh planarisation"
                deviation = deviation_flat

                if target_areas:
                    name      = "Volmesh arearisation"
                    deviation = deviation_area

                print_result(name, k, deviation)

            break

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(volmesh, k, callback_args)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   planarisation helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _pair_membership(item1, item2, container):
    if item1 in container or item2 in container:
        return True
    else:
        return False


def _get_current_mesh_normals(mesh):
    normal_dict = {}
    for fkey in mesh.face:
        center = mesh.face_center(fkey)
        normal = mesh.face_normal(fkey)
        normal_dict[fkey] = {'normal': normal, 'center': center}
    return normal_dict


def _get_current_volmesh_normals(volmesh):
    normal_dict = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_oriented_normal(hfkey)
        normal_dict[hfkey] = {'normal': normal, 'center': center}
    return normal_dict


def _avg_face_area(mesh, fkeys):
    total_area = sum(mesh.face_area(fkey) for fkey in fkeys)
    return total_area / len(fkeys)


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
