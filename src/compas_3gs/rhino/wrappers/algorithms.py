from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.helpers import volmesh_select_vertices
from compas_rhino.helpers import volmesh_select_faces

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector

from compas_rhino.conduits import FacesConduit
from compas_rhino.conduits import LinesConduit

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate
from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.operations import cell_subdivide_barycentric

from compas_3gs.utilities import volmesh_face_flatness
from compas_3gs.utilities import volmesh_face_areaness

from compas_3gs.rhino.control import volmesh3gs_select_cell
from compas_3gs.rhino.display import PlanarisationConduit
from compas_3gs.rhino.display import ReciprocationConduit

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['rhino_volmesh_planarise',
           'rhino_volmesh_reciprocate']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   planarisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_volmesh_planarise(volmesh,
                            kmax=500,

                            target_areas={},
                            target_normals={},
                            target_centers={},

                            fix_vkeys=[],

                            fix_boundary_normals=False,
                            fix_all_normals=False,
                            flat_tolerance=0.001,
                            area_tolerance=0.001,

                            fix_all=False,

                            refreshrate=5):

    # 1. callback / conduit ----------------------------------------------------
    conduit = PlanarisationConduit(volmesh)

    def callback(volmesh, k, args):

        if k % refreshrate == 0:
            conduit.face_colors = volmesh_face_flatness(volmesh)
            if target_areas:
                conduit.face_colors = volmesh_face_areaness(volmesh, target_areas)

            conduit.redraw()

    # 2. planarisation ---------------------------------------------------------
    volmesh.clear()

    with conduit.enabled():
        volmesh_planarise(volmesh,
                          kmax=kmax,
                          target_areas=target_areas,
                          target_normals=target_normals,
                          target_centers=target_centers,
                          omit_fkeys=[],
                          omit_vkeys=fix_vkeys,
                          fix_boundary_normals=fix_boundary_normals,
                          fix_all_normals=fix_all_normals,
                          flat_tolerance=flat_tolerance,
                          area_tolerance=area_tolerance,
                          callback=callback,
                          callback_args=None,
                          print_result=True)

    # 3. update / redraw -------------------------------------------------------
    volmesh.draw()


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   arearisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def rhino_volmesh_arearise(volmesh,
#                            conduit=False):

#     volmesh.clear()
#     volmesh.draw_edges()
#     volmesh.draw_faces()

#     rs.EnableRedraw(True)

#     hfkeys = volmesh_select_faces(volmesh)
#     area = rs.GetReal("Enter target area", 1000, 0)

#     target_areas = {hfkey: area for hfkey in hfkeys}

#     if conduit:
#         conduit = ArearisationConduit(volmesh, target_areas)
#         conduit.Enabled = True

#     volmesh_planarise(volmesh,
#                       count=1000,
#                       target_normals=None,
#                       target_centers=None,
#                       fix_all=False,
#                       target_areas=target_areas,
#                       fix_boundary=True)

#     if conduit:
#         conduit.Enabled = False
#         del conduit

#     volmesh.draw()


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   reciprocation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_volmesh_reciprocate(volmesh,
                              formdiagram,
                              kmax=1000,
                              weight=1,
                              edge_min=1,
                              edge_max=20,
                              fix_vkeys=[],
                              tolerance=0.00001,
                              refreshrate=5):

    # 1. callback / conduit ----------------------------------------------------
    conduit = ReciprocationConduit(volmesh,
                                   formdiagram)

    def callback(volmesh, formdiagram, k, args):
        if k % refreshrate == 0:
            conduit.redraw()

    # 2. reciprocation ---------------------------------------------------------
    volmesh.clear()
    formdiagram.clear()

    with conduit.enabled():
        volmesh_reciprocate(volmesh=volmesh,
                            formdiagram=formdiagram,
                            kmax=kmax,
                            weight=weight,
                            fix_vkeys=fix_vkeys,
                            edge_min=edge_min,
                            edge_max=edge_max,
                            tolerance=tolerance,
                            callback=callback)

    # 3. update / redraw -------------------------------------------------------
    volmesh.draw()
    formdiagram.draw()
