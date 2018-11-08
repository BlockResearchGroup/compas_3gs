from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_rhino.helpers.volmesh import volmesh_select_vertices
from compas_rhino.helpers.volmesh import volmesh_select_faces

from compas_rhino.conduits import FacesConduit
from compas_rhino.conduits import LinesConduit

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate
from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.operations import cell_subdivide_barycentric

from compas_3gs.utilities import volmesh_face_flatness


from compas_3gs_rhino.control.dynamic_pickers import volmesh3gs_select_cell

from compas_3gs_rhino.display import PlanarisationConduit
from compas_3gs_rhino.display import ArearisationConduit
from compas_3gs_rhino.display import ReciprocationConduit


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['rhino_volmesh_planarise',
           'rhino_volmesh_arearise',
           'rhino_volmesh_reciprocate']


# ==============================================================================
# ==============================================================================
# ==============================================================================
#
#   planarisation
#
# ==============================================================================
# ==============================================================================
# ==============================================================================


def rhino_volmesh_planarise(volmesh,
                        kmax=500,

                        target_areas={},
                        target_normals={},
                        target_centers={},

                        fix_boundary_normals=False,
                        fix_all_normals=False,
                        flat_tolerance=0.001,
                        area_tolerance=0.001,

                        fix_all=False,
                        conduit=False):

    # 1. select vertices to fix   ----------------------------------------------
    vkeys = volmesh_select_vertices(volmesh)

    # 2. callback / conduit ----------------------------------------------------
    conduit = PlanarisationConduit(volmesh, refreshrate=10)

    def callback(volmesh, k, args):
        conduit.face_colors = volmesh_face_flatness(volmesh)
        conduit.redraw(k)

    # 3. planarisation ---------------------------------------------------------
    volmesh.clear()

    with conduit.enabled():
        volmesh_planarise(volmesh,
                          kmax=kmax,
                          target_areas=target_areas,
                          target_normals=target_normals,
                          target_centers=target_centers,
                          omit_fkeys=[],
                          omit_vkeys=vkeys,
                          fix_boundary_normals=fix_boundary_normals,
                          fix_all_normals=fix_all_normals,
                          flat_tolerance=flat_tolerance,
                          area_tolerance=area_tolerance,
                          callback=callback,
                          callback_args=None)

    # 4. update / redraw -------------------------------------------------------
    volmesh.draw()


# ==============================================================================
# ==============================================================================
# ==============================================================================
#
#   arearisation
#
# ==============================================================================
# ==============================================================================
# ==============================================================================


def rhino_volmesh_arearise(volmesh,
                           conduit=False):

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces()

    rs.EnableRedraw(True)

    hfkeys = volmesh_select_faces(volmesh)
    area = rs.GetReal("Enter target area", 1000, 0)

    target_areas = {hfkey: area for hfkey in hfkeys}

    if conduit:
        conduit = ArearisationConduit(volmesh, target_areas)
        conduit.Enabled = True

    volmesh_planarise(volmesh,
                      count=1000,
                            target_normals=None,
                            target_centers=None,
                            fix_all=False,
                            target_areas=target_areas,
                            fix_boundary=True)

    if conduit:
        conduit.Enabled = False
        del conduit

    volmesh.draw()


# ==============================================================================
# ==============================================================================
# ==============================================================================
#
#   reciprocation
#
# ==============================================================================
# ==============================================================================
# ==============================================================================


def rhino_volmesh_reciprocate(volmesh,
                              formdiagram,
                              kmax=100,
                              edge_min=1,
                              edge_max=20,
                              fix_vkeys=[],
                              tolerance=0.00001):

    # 1. get weight ------------------------------------------------------------
    weight = rs.GetReal(
        "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)

    # 2. callback / conduit ----------------------------------------------------
    conduit = ReciprocationConduit(volmesh, formdiagram, refreshrate=1)

    def callback(volmesh, formdiagram, k, args):
        conduit.redraw(k)

    # 3. reciprocation ---------------------------------------------------------
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

    # 4. update / redraw -------------------------------------------------------
    volmesh.draw()
    formdiagram.draw()
