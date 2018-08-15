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
from compas.geometry import project_point_plane
from compas.geometry import distance_point_point

from compas_3gs.algorithms import volmesh_planarise_faces

from compas_3gs.rhino import reciprocation_conduit

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'volmesh_reciprocate',
]


def volmesh_reciprocate(volmesh,
                        formdiagram,
                        weight=None,
                        count=50,
                        min_edge=5,
                        max_edge=15,
                        tolerance=0.001):
    """Perpendicularizes the polyhedral form and force diagrams.

    Parameters
    ----------
    volmesh : VolMesh
        A mesh object.
    formdiagram : VolMesh or Network
        The type of the dual mesh.
        Defaults to the type of the provided mesh object.
    weight : float
        A float, between 0 and 1.
        Determines how much each diagram changes.
        Default is 1, where only the form diagram changes.
        Value of 0 would change the force diagram only.
    min_edge : float
        Minimum length constraint for the form diagram edges.
    max_edge : float
        Maximum length constraint for the form diagram edges.
    tolerance: float
        Sets the convergence tolerance.

    Returns
    -------
    (ForceVolMesh, FormVolMesh or FormNetwork)
        perpendicularized volmesh and formdiagram.

    """

    # ==========================================================================
    #   set weight
    # ==========================================================================
    if not weight:
        weight = rs.GetReal(
            "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)

    # ==========================================================================
    #   compute target vectors
    # ==========================================================================
    target_normals = {}
    halfface_uv    = {}
    #   for internal halffaces -------------------------------------------------
    for u, v in formdiagram.edges_iter():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        face_normal   = scale_vector(volmesh.halfface_normal(u_hfkey), weight)
        edge_vector   = scale_vector(formdiagram.edge_vector(u, v), 1 - weight)
        target_vector = normalize_vector(add_vectors(face_normal, edge_vector))
        target_normals[u_hfkey] = target_vector
        halfface_uv[u_hfkey]    = (u, v)
    # for hfkey in volmesh.halffaces_on_boundary():
    #     target_normals[hfkey] = volmesh.halfface_normal(hfkey)

    # ==========================================================================
    #   conduit
    # ==========================================================================
    conduit = reciprocation_conduit(volmesh, formdiagram)
    conduit.Enabled  = True

    # ==========================================================================
    #   loop
    # ==========================================================================

    lines = []
    polylines = []

    iteration = 1

    while count:

        form_layer = 'formdiagram-iteration.{}'.format(iteration)
        force_layer = 'forcediagram-iteration.{}'.format(iteration)

        rs.AddLayer(form_layer)
        rs.AddLayer(force_layer)

        deviation = 0

        relative_change = 0


        for fkey in volmesh.faces():
            hf_vkeys = volmesh.halfface_vertices(fkey)
            points = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            polylines.append({'points': points + [points[0]],
                              'layer' : force_layer})


        # ======================================================================
        #   FORCE DIAGRAM
        # ======================================================================
        volmesh_planarise_faces(volmesh,
                                count=1,
                                target_normals=target_normals,
                                conduit=False)

        # ======================================================================
        #   FORM DIAGRAM
        # ======================================================================
        new_formdiagram_xyz = {vkey: [] for vkey in formdiagram.vertex}

        for hfkey in halfface_uv:

            u, v          = halfface_uv[hfkey]
            target_normal = target_normals[hfkey]

            #   compute lambda : checking orientations -------------------------
            edge_vector = formdiagram.edge_vector(u, v, unitized=False)
            dot_v       = dot_vectors(normalize_vector(edge_vector), target_normal)
            if dot_v < 0:
                target_normal = scale_vector(target_normal, -1)

            #   check perpendicularity status ----------------------------------
            perp_check = abs(1 - abs(dot_v))

            if perp_check > deviation:
                deviation = perp_check

            #   target edge length -----------------------------------------
            dist = length_vector(edge_vector)
            if dist < min_edge:
                dist = min_edge
            if dist > max_edge:
                dist = max_edge

            #   compute and add new xyz for v ------------------------------
            new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_normal, -1 * dist))
            new_formdiagram_xyz[u].append(new_u_xyz)
            new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_normal, dist))
            new_formdiagram_xyz[v].append(new_v_xyz)

        # ======================================================================
        #   UPDATE
        # ======================================================================
        for vkey in new_formdiagram_xyz:
            if new_formdiagram_xyz[vkey]:
                initial_xyz = formdiagram.vertex_coordinates(vkey)
                final_xyz = centroid_points(new_formdiagram_xyz[vkey])
                formdiagram.vertex_update_xyz(vkey, final_xyz)

                iteration_change = distance_point_point(initial_xyz, final_xyz)
                if iteration_change > relative_change:
                    relative_change = iteration_change

        # ======================================================================
        #   DRAWING
        # ======================================================================





        for u, v in formdiagram.edges_iter():
            lines.append({'start' : formdiagram.vertex_coordinates(u),
                          'end'   : formdiagram.vertex_coordinates(v),
                          'layer' : form_layer})

        # ======================================================================
        #   EVALUATE
        # ======================================================================
        if deviation < tolerance:
            break


        sc.doc.Views.Redraw()
        count     -= 1
        iteration += 1

    # ==========================================================================
    #   END
    # ==========================================================================
    conduit.Enabled = False
    # conduit.Dispose()
    del conduit

    # compas_rhino.xdraw_lines(lines)
    # compas_rhino.xdraw_polylines(polylines)

    print('reciprocation ended at:', iteration)
    print('deviation:', deviation)

    volmesh.draw(layer='forcepolyhedra')
    formdiagram.draw(layer='formdiagram')


def _OLD_volmesh_reciprocate(volmesh,
                             formdiagram,
                             weight=1,
                             count=500,
                             min_edge=5,
                             max_edge=50,
                             tolerance=0.001):
    """Perpendicularizes the polyhedral form and force diagrams.

    Parameters
    ----------
    volmesh : VolMesh
        A mesh object.
    formdiagram : VolMesh or Network
        The type of the dual mesh.
        Defaults to the type of the provided mesh object.
    weight : float
        A float, between 0 and 1.
        Determines how much each diagram changes.
        Default is 1, where only the form diagram changes.
        Value of 0 would change the force diagram only.
    min_edge : float
        Minimum length constraint for the form diagram edges.
    max_edge : float
        Maximum length constraint for the form diagram edges.
    tolerance: float
        Sets the convergence tolerance.

    Returns
    -------
    perpendicularized volmesh and formdiagram.

    """

    # ==========================================================================
    #   compute target vectors
    # ==========================================================================
    target_normals = {}
    halfface_uv    = {}
    #   for internal halffaces -------------------------------------------------
    for u, v in formdiagram.edges_iter():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        face_normal   = scale_vector(volmesh.halfface_normal(u_hfkey), weight)
        edge_vector   = scale_vector(formdiagram.edge_vector(u, v), 1 - weight)
        target_vector = add_vectors(face_normal, edge_vector)
        target_normals[u_hfkey] = normalize_vector(target_vector)
        halfface_uv[u_hfkey]    = (u, v)
    for hfkey in volmesh.halffaces_on_boundary():
        target_normals[hfkey] = volmesh.halfface_normal(hfkey)

    # ==========================================================================
    #   conduit
    # ==========================================================================
    conduit = reciprocation_conduit(volmesh, formdiagram)
    conduit.Enabled  = True

    # ==========================================================================
    #   loop
    # ==========================================================================
    iteration = 0

    while count:

        deviation = 0

        new_volmesh_xyz     = {vkey: [] for vkey in volmesh.vertex}
        new_formdiagram_xyz = {vkey: [] for vkey in formdiagram.vertex}

        for hfkey in target_normals:

            target_normal = target_normals[hfkey]

            # ==================================================================
            #   FOCE DIAGRAM
            # ==================================================================

            dot_v = dot_vectors(volmesh.halfface_normal(hfkey), target_normal)
            perp_check = abs(1 - abs(dot_v))
            if perp_check > deviation:
                deviation = perp_check

            plane    = (volmesh.halfface_center(hfkey), target_normal)
            for vkey in volmesh.halfface_vertices(hfkey):
                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                new_volmesh_xyz[vkey].append(new_xyz)

            # ==================================================================
            #   FORM DIAGRAM
            # ==================================================================
            if hfkey in halfface_uv:
                u, v = halfface_uv[hfkey]
                #   checking orientations --------------------------------------
                edge_vector = formdiagram.edge_vector(u, v, unitized=False)
                dot_v       = dot_vectors(normalize_vector(edge_vector), target_normal)
                if dot_v < 0:
                    target_normal = scale_vector(target_normal, -1)
                #   check perpendicularity status ------------------------------
                perp_check = abs(1 - abs(dot_v))
                if perp_check > deviation:
                    deviation = perp_check
                #   target edge length -----------------------------------------
                dist = length_vector(edge_vector)
                if dist < min_edge:
                    dist = min_edge
                if dist > max_edge:
                    dist = max_edge
                #   compute and add new xyz for v ------------------------------
                new_u_xyz = add_vectors(formdiagram.vertex_coordinates(v), scale_vector(target_normal, -1 * dist))
                new_formdiagram_xyz[u].append(new_u_xyz)
                new_v_xyz = add_vectors(formdiagram.vertex_coordinates(u), scale_vector(target_normal, dist))
                new_formdiagram_xyz[v].append(new_v_xyz)

        # ======================================================================
        #   UPDATE
        # ======================================================================
        for vkey in new_volmesh_xyz:
            if new_volmesh_xyz[vkey]:
                final_xyz = centroid_points(new_volmesh_xyz[vkey])
                volmesh.vertex_update_xyz(vkey, final_xyz)
        for vkey in new_formdiagram_xyz:
            if new_formdiagram_xyz[vkey]:
                final_xyz = centroid_points(new_formdiagram_xyz[vkey])
                formdiagram.vertex_update_xyz(vkey, final_xyz)

        # ======================================================================
        #   EVALUATE
        # ======================================================================
        if deviation < tolerance:
            break
        sc.doc.Views.Redraw()
        count     -= 1
        iteration += 1

    # ==========================================================================
    #   END
    # ==========================================================================
    conduit.Enabled = False
    del conduit

    print('reciprocation ended at:', iteration)
    print('deviation:', deviation)

    volmesh.draw()
    formdiagram.draw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
