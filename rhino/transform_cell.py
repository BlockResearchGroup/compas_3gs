import System.Drawing.Color
from System.Drawing.Color import FromArgb
import scriptcontext as sc

import ast

import Rhino
import rhinoscriptsyntax as rs

from Rhino.Geometry import Vector3d
from Rhino.Geometry import Point3d


from compas.geometry import intersection_line_plane

from compas_rhino.helpers.selectors import FaceSelector

from compas_3gs.helpers import sort_points_ccw


feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color = System.Drawing.Color.FromArgb(255, 0, 79)
find_object = sc.doc.Objects.Find


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell transformations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_pull_face(volmesh):

    if len(volmehs.cell) > 1:
        print("too many cells in this volmesh!")
        return

    volmesh_faceselect = FaceSelector(volmesh)
    hfkey = volmesh_faceselect.select_face()

    if hfkey is None:
        return

    # face info ----------------------------------------------------------------
    normal = volmesh.halfface_normal(hfkey)
    center = volmesh.halfface_center(hfkey)
    vkeys  = volmesh.halfface_vertices(hfkey, ordered=True)

    # face vertices ------------------------------------------------------------
    v_xyz  = {}
    v_nbrs = {}
    for vkey in vkeys:
        v_xyz[vkey] = volmesh.vertex_coordinates(vkey)
        nbr_vkeys   = []
        for nbr_vkey in volmesh.vertex_neighbours(vkey):
            if nbr_vkey not in vkeys:
                nbr_vkeys.append(nbr_vkey)
        v_nbrs[vkey] = nbr_vkeys

    # sort nbr vertices --------------------------------------------------------
    all_nbrs = [nbr_vkey for nbr_vkey_list in v_nbrs.values() for nbr_vkey in nbr_vkey_list]
    nbr_xyz = {nbr_key: volmesh.vertex_coordinates(vkey) for vkey in all_nbrs}
    ordered_nbr_vkeys = sort_points_ccw(nbr_xyz, (center, normal))

    rs.EnableRedraw(True)

    # ==========================================================================
    #   rhino dynamic draw
    # ==========================================================================
    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        plane = (cp, normal)

        new_xyz = {}

        for vkey in v_xyz:
            for nbr_vkey in v_nbrs[vkey]:
                sp = v_xyz[vkey]
                ep = nbr_xyz[nbr_vkey]
                ip = intersection_line_plane((sp, ep), plane)
                n

        # for vkey in v_xyz:
        #     for nbr_vkey in





















    normal = Rhino.Geometry.Vector3d(*normal)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#  helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _cell_vertex_normal(volmesh, vkey):
    if len(volmehs.cell) > 1:
        print("too many cells in this volmesh!")
        return
    faces = volmesh.vertex_halffaces(vkey)


    pass


def _cell_vertex_neighbours(volmesh, vkey, ordered=True):
    if len(volmehs.cell) > 1:
        print("too many cells in this volmesh!")
        return
    pass


def _cell_face_neighbours(volmesh, hfkey, ordered=True):
    pass
















# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   rhino helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _get_initial_point(message='Point to move from?'):
    ip = Rhino.Input.Custom.GetPoint()
    ip.SetCommandPrompt(message)
    ip.Get()
    ip = ip.Point()
    return ip


def _get_target_point(constraint, OnDynamicDraw, option='None', message='Point to move to?'):
    gp = Rhino.Input.Custom.GetPoint()
    gp.SetCommandPrompt(message)
    if option == 'None':
        gp.Constrain(constraint)
    if option != 'None':
        gp.Constrain(constraint, option)
    gp.DynamicDraw += OnDynamicDraw
    gp.Get()
    gp = gp.Point()
    return gp








