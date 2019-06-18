from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import math
import compas

from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import centroid_polygon
from compas.geometry import intersection_line_plane

from compas.utilities import i_to_rgb

from compas_rhino.utilities import draw_lines
from compas_rhino.utilities import draw_labels

from compas_rhino.helpers import mesh_select_face
from compas_rhino.helpers import volmesh_select_face

from compas_3gs.operations import cell_split_indet_face_vertices
from compas_3gs.operations import cell_relocate_face

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented
from compas_3gs.utilities import datastructure_centroid

from compas_3gs.rhino import get_target_point

try:
    import System
    import Rhino
    import scriptcontext as sc
    import rhinoscriptsyntax as rs

    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Vector3d
    from Rhino.Geometry import Line

    from System.Drawing.Color import FromArgb

    find_object    = sc.doc.Objects.Find
    feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
    arrow_color    = FromArgb(255, 0, 79)
    jl_blue        = FromArgb(0, 113, 188)
    black          = FromArgb(0, 0, 0)
    gray           = FromArgb(200, 200, 200)
    green          = FromArgb(0, 255, 0)
    white          = FromArgb(255, 255, 255)

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['rhino_cell_face_pull_interactive']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell transformations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_cell_face_pull_interactive(cell):

    # --------------------------------------------------------------------------
    #  1. pick face
    # --------------------------------------------------------------------------
    cell.draw()
    face = mesh_select_face(cell)
    cell_split_indet_face_vertices(cell, face)
    cell.clear()

    # --------------------------------------------------------------------------
    #  2. face data
    # --------------------------------------------------------------------------
    f_normal = cell.face_normal(face)
    f_center = cell.face_center(face)
    f_area   = cell.face_area(face)
    f_vkeys  = cell.face_vertices(face)

    # --------------------------------------------------------------------------
    #  3. get neighbor edges and vertex coordinates
    # --------------------------------------------------------------------------
    edges = {}
    for u in f_vkeys:
        u_nbrs = cell.vertex_neighbors(u)
        for v in u_nbrs:
            if v not in f_vkeys:
                edges[u] = v

    xyz_dict = {}
    for vkey in cell.vertex:
        if vkey not in f_vkeys:
            xyz_dict[vkey] = cell.vertex_coordinates(vkey)

    # --------------------------------------------------------------------------
    #  4. dynamic draw
    # --------------------------------------------------------------------------
    rs.EnableRedraw(True)

    def OnDynamicDraw(sender, e):

        cp          = e.CurrentPoint
        plane       = (cp, f_normal)
        new_pt_list = []

        for u in f_vkeys:
            v           = edges[u]
            u_xyz       = cell.vertex_coordinates(u)
            v_xyz       = cell.vertex_coordinates(v)
            line        = (u_xyz, v_xyz)
            it          = intersection_line_plane(line, plane)
            xyz_dict[u] = it
            new_pt_list.append(it)

            e.Display.DrawDottedLine(
                Point3d(*u_xyz),
                Point3d(*it),
                feedback_color)

        for vkey in cell.vertex:
            xyz = cell.vertex_coordinates(vkey)
            e.Display.DrawPoint(Point3d(*xyz), 0, 5, black)

        # old normal and area --------------------------------------------------
        e.Display.DrawDot(Point3d(*f_center),
                          str(round(f_area, 3)),
                          gray, white)

        # draw original face ---------------------------------------------------
        for i in range(-1, len(f_vkeys) - 1):
            vkey1 = f_vkeys[i]
            vkey2 = f_vkeys[i + 1]
            sp    = Point3d(*cell.vertex_coordinates(vkey1))
            np    = Point3d(*cell.vertex_coordinates(vkey2))

            e.Display.DrawDottedLine(sp, np, feedback_color)

        # get current face info ------------------------------------------------
        areas   = {}
        normals = {}
        for fkey in cell.faces():
            face_coordinates = [xyz_dict[vkey] for vkey in cell.face_vertices(fkey)]
            areas[fkey]   = polygon_area_oriented(face_coordinates)
            normals[fkey] = polygon_normal_oriented(face_coordinates)

        # draw new face areas / vectors ----------------------------------------
        for fkey in cell.faces():
            area   = areas[fkey]
            normal = normals[fkey]
            value  = area / max(areas.values())
            color  = i_to_rgb(value)
            color  = System.Drawing.Color.FromArgb(*color)

            # draw vectors -----------------------------------------------------
            scale  = 0.25
            center = datastructure_centroid(cell)
            sp     = Point3d(*center)
            vector = scale_vector(normal, area * scale)
            ep     = Point3d(*add_vectors(center, vector))

            e.Display.DrawArrow(Line(sp, ep), color, 20, 0)

            # draw face --------------------------------------------------------
            face_coordinates = [xyz_dict[vkey] for vkey in cell.face_vertices(fkey)]
            face_coordinates.append(face_coordinates[0])
            polygon_xyz   = [Point3d(*xyz) for xyz in face_coordinates]

            e.Display.DrawPolyline(polygon_xyz, black, 2)

            if fkey == face:
                e.Display.DrawPolyline(polygon_xyz, black, 4)
                e.Display.DrawPolygon(polygon_xyz, color, filled=True)

            # display force magnitudes -----------------------------------------
            vector = add_vectors(vector,
                                 scale_vector(normalize_vector(normal), 0.75))
            xyz    = add_vectors(center, vector)
            if fkey == face:
                color = black

            e.Display.DrawDot(Point3d(*xyz), str(round(area, 2)), color, white)

    # --------------------------------------------------------------------------
    #  5. input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*f_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*f_normal))
    gp   = get_target_point(line, OnDynamicDraw)

    # --------------------------------------------------------------------------
    #  6. update cell coordinates
    # --------------------------------------------------------------------------
    cell_relocate_face(cell, face, gp, f_normal)

    cell.draw()


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _evaluate_trial_face_area(volmesh, hfkey, new_xyz):
    hf_vkeys = volmesh.halfface_vertices(hfkey)
    points   = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
    normal   = volmesh.halfface_oriented_normal(hfkey)

    edges    = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v
    new_plane   = (new_xyz, volmesh.halfface_oriented_normal(hfkey))
    new_pt_list = []
    for u in hf_vkeys:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, new_plane)
        new_pt_list.append(it)

    new_normal = polygon_normal_oriented(new_pt_list, unitized=False)
    new_area = length_vector(new_normal)

    sign = 1
    if dot_vectors(normal, new_normal) < 0:
        sign = -1

    return new_area * sign


def _get_move_direction(volmesh, hfkey):
    normal     = volmesh.halfface_oriented_normal(hfkey)
    center     = volmesh.halfface_center(hfkey)
    area       = volmesh.halfface_oriented_area(hfkey)
    new_center = add_vectors(center, normal)
    new_area = _evaluate_trial_face_area(volmesh, hfkey, new_center)

    print('new_area', new_area)
    print('area', area)

    if new_area > area:
        move_dir = 1
    if new_area < area:
        move_dir = -1
    if new_area == area:
        raise ValueError('The face already has target area!')

    print(move_dir)

    return move_dir


# def _cell_draw_current(volmesh, hfkey, center, iteration, color):

#     lines = []

#     name = 'iteration-{}'.format(iteration)
#     rs.AddLayer('iteration-{}'.format(iteration))

#     hf_vkeys = volmesh.halfface_vertices(hfkey)
#     points   = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
#     normal   = polygon_normal_oriented(points)

#     edges    = {}
#     for u in hf_vkeys:
#         u_nbrs = volmesh.vertex_neighbours(u)
#         for v in u_nbrs:
#             if v not in hf_vkeys:
#                 edges[u] = v
#     new_plane   = (center, volmesh.halfface_oriented_normal(hfkey))
#     new_pt_list = []

#     for u in hf_vkeys:
#         v     = edges[u]
#         u_xyz = volmesh.vertex_coordinates(u)
#         v_xyz = volmesh.vertex_coordinates(v)
#         line  = (u_xyz, v_xyz)
#         it    = intersection_line_plane(line, new_plane)
#         new_pt_list.append(it)

#         lines.append({
#             'start': u_xyz,
#             'end'  : it,
#             # 'arrow': 'end',
#             'color': color,
#             'layer': name,
#             'name' : 'iteration.{}'.format(iteration)})

#     new_normal = polygon_normal_oriented(new_pt_list, unitized=False)
#     new_area = length_vector(new_normal)

#     for i in range(-1, len(new_pt_list) - 1):
#         a = new_pt_list[i]
#         b = new_pt_list[i + 1]

#         lines.append({
#             'start': a,
#             'end'  : b,
#             # 'arrow': 'end',
#             'color': color,
#             'layer': name,
#             'name' : 'iteration-{}.area-{}'.format(iteration, new_area)})

#     new_normal = polygon_normal_oriented(new_pt_list, unitized=False)
#     new_area = length_vector(new_normal)

#     draw_lines(lines)


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
