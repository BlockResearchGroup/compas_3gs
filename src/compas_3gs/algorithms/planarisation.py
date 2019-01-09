from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry.transformations.transformations import project_point_plane

from compas_3gs.utilities import scale_polygon


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'volmesh_planarise'
]


def volmesh_planarise(volmesh,
                      kmax=100,
                      target_areas={},
                      target_normals={},
                      target_centers={},
                      omit_fkeys=[],
                      omit_vkeys=[],
                      fix_boundary_normals=False,
                      fix_all_normals=False,
                      flat_tolerance=0.001,
                      area_tolerance=0.001,
                      callback=None,
                      callback_args=None,
                      print_result=False):
    """Planarisation of volmesh faces.

    Planarisation is implemented as a two-stp iterative procedure. At every iteration, faces are first individually projected to their best-fit plane,
    and then the vertices are projected to the centroid of the disconnected
    corners of the faces.

    Specific target_areas


    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object.
    kmax : int, optional [100]
        Maximum number of iterations.
        Default is ``1``.
    target_face_areas : dictionary, optional [{}]
        A dictionary of fkeys and target areas.
    target_face_normals : dictionary, optional [{}]
        A dictionary of fkeys and target face normals.
    target_face_centers : dictionary, optional [{}]
        A dictionary of fkeys and target face centers.
    omit_fkeys : list, optional [[]]
        List of fkeys to omit from planarising.
    fix_boundary_face_normals : boolean, optional [False]
        Whether to keep the initial normals of the bondary faces.
    fix_all_face_normals : boolean, optional [False]
        Whether to keep the initial normals of all faces.
    flat_tolerance: float, optional
        Convergence tolerance for face flatness.
    area_tolerance: float, optional
        Convergence tolerance for face areas.
    callback : callable, optional
        A user-defined callback function to be executed after every iteration.
        Default is ``None``.
    callback_args : tuple, optional
        Additional parameters to be passed to the callback.
        Default is ``None``.

    See Also
    --------
    * :func:`compas.geometry.mesh_planarize_faces`

    """

    if callback:
        if not callable(callback):
            raise Exception('Callback is not callable.')

    # --------------------------------------------------------------------------
    #   1. initialise
    # --------------------------------------------------------------------------
    free_vkeys      = list(set(volmesh.vertex) - set(omit_vkeys))
    initial_normals = _get_current_normals(volmesh)
    boundary_fkeys  = set(volmesh.halffaces_boundary())

    # --------------------------------------------------------------------------
    #   2. loop
    # --------------------------------------------------------------------------
    for k in range(kmax):

        flat_deviation = 0
        area_deviation = 0

        new_xyz = {vkey: [] for vkey in volmesh.vertex}

        for fkey in volmesh.faces():

            fkey_pair = volmesh.halfface_pair(fkey)

            # 1. evaluate current face -----------------------------------------
            f_vkeys  = volmesh.halfface_vertices(fkey)
            f_center = volmesh.halfface_center(fkey)
            f_normal = volmesh.halfface_normal(fkey)
            f_area   = volmesh.halfface_area(fkey)

            # 2. override with manual target values ----------------------------
            if _pair_membership(fkey, fkey_pair, target_centers):
                f_center = target_centers[fkey]
            if _pair_membership(fkey, fkey_pair, target_normals):
                f_normal = target_normals[fkey]
            if fix_boundary_normals:
                if _pair_membership(fkey, fkey_pair, boundary_fkeys):
                    f_normal = initial_normals[fkey]['normal']
            if fix_all_normals:
                f_normal = initial_normals[fkey]['normal']

            # 3. projection plane ----------------------------------------------
            plane = (f_center, f_normal)

            # 4. planarise -----------------------------------------------------
            new_face = {}
            for vkey in f_vkeys:
                xyz            = volmesh.vertex_coordinates(vkey)
                projected_xyz  = project_point_plane(xyz, plane)
                new_face[vkey] = projected_xyz
                dist           = distance_point_point(xyz, projected_xyz)
                if dist > flat_deviation:
                    flat_deviation = dist

            # 5. arearise ------------------------------------------------------
            if fkey in target_areas:
                target_area = target_areas[fkey]
                scale       = (target_area / f_area) ** 0.5
                new_face    = scale_polygon(new_face, scale)

                areaness  = abs(f_area - target_area)
                if areaness > area_deviation:
                    area_deviation = areaness

            # 6. collect new coordinates ---------------------------------------
            for vkey in new_face:
                new_xyz[vkey].append(new_face[vkey])

        # 7. compute new coordinates
        for vkey in free_vkeys:
            final_xyz = centroid_points(new_xyz[vkey])
            volmesh.vertex_update_xyz(vkey, final_xyz)

        # 8. check convergence -------------------------------------------------
        if flat_deviation < flat_tolerance and area_deviation < area_tolerance:
            break

        # callback / conduit ---------------------------------------------------
        if callback:
            callback(volmesh, k, callback_args)

    # --------------------------------------------------------------------------
    #   3. print result
    # --------------------------------------------------------------------------
    if print_result:
        text = "Planarisation"
        if target_areas:
            text = "Arearisation"
        print('==============================================================')
        print('')
        print(text, 'stopped after', k, 'iterations ...')
        print('... with flatness deviation of :', flat_deviation)
        print('... with areaness deviation of :', area_deviation)
        print('')
        print('==============================================================')


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


def _get_current_normals(volmesh):
    normal_dict = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        normal_dict[hfkey] = {'normal': normal, 'center': center}
    return normal_dict




# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
