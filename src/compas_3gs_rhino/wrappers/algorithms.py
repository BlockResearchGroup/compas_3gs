

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate
from compas_3gs.algorithms import volmesh_planarise_faces

from compas_3gs.operations import cell_subdivide_barycentric

from compas_rhino.helpers.volmesh import volmesh_select_vertices
from compas_rhino.helpers.volmesh import volmesh_select_faces

from compas_3gs_rhino.control.dynamic_pickers import volmesh3gs_select_cell

from compas_3gs_rhino.display import planarisation_conduit
from compas_3gs_rhino.display import arearisation_conduit
from compas_3gs_rhino.display import reciprocation_conduit

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


__all__ = ['rhino_planarisation',
           'rhino_arearisation',
           'rhino_reciprocation']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   planarisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_planarisation(volmesh,
                        conduit=False):

    vkeys = volmesh_select_vertices(volmesh)

    if conduit:
        conduit = planarisation_conduit(volmesh)
        conduit.Enabled = True

    volmesh_planarise_faces(volmesh,
                            count=1000,
                            target_normals=None,
                            target_centers=None,
                            fix_boundary=False,
                            omit_vkeys=vkeys)

    if conduit:
        conduit.Enabled = False
        del conduit

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


def rhino_arearisation(volmesh,
                       conduit=False):

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces()



    rs.EnableRedraw(True)

    hfkeys = volmesh_select_faces(volmesh)
    area = rs.GetReal("Enter target area", 1000, 0)

    target_areas = {hfkey: area for hfkey in hfkeys}

    if conduit:
        conduit = arearisation_conduit(volmesh, target_areas)
        conduit.Enabled = True

    volmesh_planarise_faces(volmesh,
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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   reciprocation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_reciprocation(volmesh,
                        formdiagram,
                        weight=1,
                        count=100,
                        min_edge=1,
                        max_edge=20,
                        fix_vkeys=[],
                        tolerance=0.00001,
                        conduit=False):

    weight = rs.GetReal(
        "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)

    if conduit:
        conduit = reciprocation_conduit(volmesh, formdiagram)
        conduit.Enabled = True

    volmesh_reciprocate(volmesh=volmesh,
                        formdiagram=formdiagram,
                        weight=weight,
                        count=count,
                        min_edge=min_edge,
                        max_edge=max_edge,
                        fix_vkeys=[],
                        tolerance=0.001)

    if conduit:
        conduit.Enabled = False
        del conduit

    volmesh.draw()
    formdiagram.draw()
