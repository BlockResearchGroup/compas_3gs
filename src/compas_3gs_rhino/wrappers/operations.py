from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

import System.Drawing.Color
from System.Drawing.Color import FromArgb

import ast

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import centroid_polyhedron
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point
from compas.geometry import centroid_points

from compas_rhino.helpers.volmesh import volmesh_select_vertices

from compas_3gs.operations import vertex_merge
from compas_3gs.operations import vertex_lift
from compas_3gs.operations import halfface_pinch
from compas_3gs.operations import halfface_merge

from compas.utilities import i_to_rgb

from compas_3gs_rhino.control.inspectors import VolmeshVertexInspector
from compas_3gs_rhino.control.inspectors import VolmeshHalffaceInspector
from compas_3gs_rhino.control.inspectors import VolmeshCellInspector

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector
from compas_3gs_rhino.control import CellSelector

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_vertices
from compas_rhino.helpers.volmesh import volmesh_select_face

from compas_3gs_rhino.control.selectors import select_boundary_halffaces

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate

from compas_3gs.utilities import normal_polygon_general
from compas_3gs.utilities import area_polygon_general

from compas_3gs.operations import cell_subdivide_barycentric

from compas_3gs_rhino.control.dynamic_pickers import volmesh3gs_select_cell

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_labels

from compas_rhino.conduits import LinesConduit


try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()

from Rhino.Geometry import Point3d
from Rhino.Geometry import Arc
from Rhino.Geometry import ArcCurve
from Rhino.Geometry import Sphere
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Plane
from Rhino.Geometry import Brep
from Rhino.Geometry import Line

find_object    = sc.doc.Objects.Find
feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color    = System.Drawing.Color.FromArgb(255, 0, 79)
jl_blue        = System.Drawing.Color.FromArgb(0, 113, 188)
black          = System.Drawing.Color.FromArgb(0, 0, 0)
gray           = System.Drawing.Color.FromArgb(200, 200, 200)
green          = System.Drawing.Color.FromArgb(0, 255, 0)
white          = System.Drawing.Color.FromArgb(255, 255, 255)


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['rhino_vertex_merge',
           'rhino_vertex_lift',
           'rhino_halfface_pinch',
           'rhino_halfface_merge',
           'rhino_cell_subdivide_barycentric',
           'volmesh_pull_faces']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   vertices
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

def rhino_vertex_merge(volmesh):

    volmesh.draw()

    keys = volmesh_select_vertices(volmesh)
    xyz   = centroid_points([volmesh.vertex_coordinates(key) for key in keys])

    vertex_merge(volmesh, keys, xyz)
    volmesh.draw()


def rhino_vertex_lift(volmesh):

    volmesh.draw()

    vkey   = volmesh_select_vertex(volmesh)

    print(volmesh.vertex_halffaces(vkey))

    boundary_hfkeys = []
    for hfkey in volmesh.vertex_halffaces(vkey):
        if volmesh.is_face_boundary(hfkey):
            boundary_hfkeys.append(hfkey)

    xyz    = volmesh.vertex_coordinates(vkey)
    normal = volmesh.vertex_normal(vkey)



    rs.EnableRedraw(True)


    def OnDynamicDraw(sender, e):

        cp     = e.CurrentPoint

        for hfkey in boundary_hfkeys:
            for vkey in volmesh.halfface_vertices(hfkey):
                sp = volmesh.vertex_coordinates(vkey)
                e.Display.DrawLine(Point3d(*sp), cp, black, 2)


    ip    = Point3d(*xyz)
    axis  = Rhino.Geometry.Line(ip, ip + Vector3d(*normal))
    gp    = _get_target_point(axis, OnDynamicDraw)

    vertex_lift(volmesh, vkey, boundary_hfkeys, gp)

    volmesh.draw()

    return volmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   faces
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_halfface_pinch(volmesh):
    hfkeys = select_boundary_halffaces(volmesh)

    key = hfkeys[0]

    center = volmesh.halfface_center(key)
    normal = volmesh.halfface_normal(key)
    line   = (center, add_vectors(center, normal))
    # --------------------------------------------------------------------------
    #  dynamic draw
    # --------------------------------------------------------------------------
    rs.EnableRedraw(True)

    def OnDynamicDraw(sender, e):

        cp     = e.CurrentPoint
        plane  = (cp, normal)
        line   = (center, add_vectors(center, normal))
        it     = intersection_line_plane(line, plane)

        translation = subtract_vectors(it, center)
        dot = dot_vectors(normal, translation)
        dot = dot / abs(dot)

        dist = distance_point_point(center, it) * dot

        for hfkey in hfkeys:
            hf_center = volmesh.halfface_center(hfkey)
            hf_normal = volmesh.halfface_normal(hfkey)
            ep = add_vectors(hf_center, scale_vector(hf_normal, dist))
            e.Display.DrawDottedLine(Point3d(*hf_center), Point3d(*ep), feedback_color)
            e.Display.DrawPoint(Point3d(*ep), 0, 4, black)
            for vkey in volmesh.halfface_vertices(hfkey):
                sp = volmesh.vertex_coordinates(vkey)
                e.Display.DrawLine(Point3d(*sp), Point3d(*ep), black, 2)

    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip    = Point3d(*center)
    axis  = Rhino.Geometry.Line(ip, ip + Vector3d(*normal))
    gp    = _get_target_point(axis, OnDynamicDraw)

    plane = (gp, normal)
    it    = intersection_line_plane(line, plane)

    translation = subtract_vectors(it, center)
    dot = dot_vectors(normal, translation)
    dot = dot / abs(dot)

    rise  = distance_point_point(center, it) * dot

    for hfkey in hfkeys:
        hf_center = volmesh.halfface_center(hfkey)
        hf_normal = volmesh.halfface_normal(hfkey)
        ep = add_vectors(hf_center, scale_vector(hf_normal, rise))

        halfface_pinch(volmesh, hfkey, ep)

    volmesh.draw()

    return volmesh


def rhino_halfface_merge(volmesh):
    volmesh.draw()
    hfkeys = select_boundary_halffaces(volmesh)
    halfface_merge(volmesh, hfkeys)
    volmesh.draw()
    return volmesh






# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def volmesh_pull_faces(volmesh, uniform=False):

    cell_colors = {}
    ckeys = volmesh.cell.keys()
    for index, ckey in enumerate(ckeys):
        value  = float(index) / (len(ckeys) - 1)

        color  = i_to_rgb(value)
        cell_colors[ckey] = color

    # 1. pick cell -------------------------------------------------------------

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces()
    volmesh.draw_cell_labels(colors=True)
    rs.EnableRedraw(True)

    # dynamic selector
    cell_inspector = VolmeshCellInspector(volmesh, color_dict=cell_colors)
    cell_inspector.enable()
    ckey = CellSelector.select_cell(volmesh)
    cell_inspector.disable()
    del cell_inspector

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_cell(ckey)
    rs.EnableRedraw(True)

    # 2. pick halfface ---------------------------------------------------------
    cell_hfkeys = volmesh.cell_halffaces(ckey)
    halfface_inspector = VolmeshHalffaceInspector(volmesh,
                                                  hfkeys=cell_hfkeys,
                                                  dependents=True)
    halfface_inspector.enable()
    hfkey = volmesh_select_face(volmesh)
    halfface_inspector.disable()
    del halfface_inspector

    dep_hfkeys = volmesh.volmesh_all_dependent_halffaces(hfkey)

    # --------------------------------------------------------------------------

    volmesh.clear()
    volmesh.draw_faces()
    rs.EnableRedraw(True)

    # 3. move face -------------------------------------------------------------
    hf_vkeys    = volmesh.halfface_vertices(hfkey)
    hf_normal   = volmesh.halfface_normal(hfkey)
    hf_center   = volmesh.halfface_center(hfkey)
    hf_area     = volmesh.halfface_area(hfkey)

    cell_vkeys = volmesh.cell_vertices(ckey)
    cell_center = volmesh.cell_centroid(ckey)

    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v in cell_vkeys:
                if v not in hf_vkeys:
                    edges[u] = v

    xyz_dict = {}
    for vkey in cell_vkeys:
        xyz_dict[vkey] = volmesh.vertex_coordinates(vkey)

    if uniform:
        hfkeys = dep_hfkeys + [hfkey]
        target_normal = _halffaces_avg_normals(volmesh, hfkeys)
    else:
        target_normal = None


    # --------------------------------------------------------------------------

    def OnDynamicDraw(sender, e):
        cp          = e.CurrentPoint

        xyz = _volmesh_compute_dependent_face_intersections(volmesh, hfkey, cp, target_normal)

        seen = set()
        for face_key in dep_hfkeys + [hfkey]:
            hf_edges   = volmesh.halfface_edges(face_key)
            for edge in hf_edges:
                u = edge[0]
                v = edge[1]
                pair = frozenset([u, v])
                if pair not in seen:
                    init_u = volmesh.vertex_coordinates(u)
                    init_u_xyz = Point3d(*init_u)
                    u_xyz = Point3d(*xyz[u])
                    v_xyz = Point3d(*xyz[v])
                    e.Display.DrawLine(Line(u_xyz, v_xyz), black, 5)
                    # e.Display.DrawDottedLine(init_u_xyz, u_xyz, feedback_color)
                    seen.add(pair)

        for u, v in volmesh.edges_iter():
            if frozenset([u, v]) not in seen:
                sp  = volmesh.vertex_coordinates(u)
                ep  = volmesh.vertex_coordinates(v)
                if u in xyz:
                    sp = xyz[u]
                if v in xyz:
                    ep = xyz[v]
                e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), black, 2)




    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*hf_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
    gp   = _get_target_point(line, OnDynamicDraw)


    # if uniform:
    #     listIndex = 3
    #     gp.AddOptionList("target_ plane", ["avg", "world", "custom"], listIndex)




    # while True:
    #     get_rc = gp.Get()
    #     gp.DynamicDraw += OnDynamicDraw
    #     # loop until a point is picked -----------------------------------------
    #     if gp.CommandResult() != Rhino.Commands.Result.Success:
    #         break
    #     if get_rc == Rhino.Input.GetResult.Option:  # keep picking options
    #         continue
    #     # loop until a point is picked -----------------------------------------
    #     elif get_rc == Rhino.Input.GetResult.Point:
    #         target = gp.Point()
    #     break




    new_xyz = _volmesh_compute_dependent_face_intersections(volmesh, hfkey, gp, target_normal)

    for key in new_xyz:
        coordinates = new_xyz[key]
        volmesh.vertex_update_xyz(key, coordinates, constrained=False)

    volmesh.clear()
    volmesh.clear_cell_labels()
    volmesh.draw()




# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_cell_subdivide_barycentric(volmesh, formdiagram=None):


    cell_colors = {}
    ckeys = volmesh.cell.keys()
    for index, ckey in enumerate(ckeys):
        color = (0, 0, 0)
        if len(ckeys) != 1:
            value  = float(index) / (len(ckeys) - 1)
            color  = i_to_rgb(value)
        cell_colors[ckey] = color

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces()
    volmesh.draw_cell_labels(colors=True)
    rs.EnableRedraw(True)

    # dynamic selector
    cell_inspector = VolmeshCellInspector(volmesh, color_dict=cell_colors)
    cell_inspector.enable()
    sel_ckeys = CellSelector.select_cells(volmesh)
    cell_inspector.disable()
    del cell_inspector
    volmesh.clear_cell_labels()


    for ckey in sel_ckeys:
        cell_subdivide_barycentric(volmesh, ckey)


    # if formdiagram:
    #     xyz = {vkey: formdiagram.vertex_coordinates(vkey) for vkey in formdiagram.vertex}

    #     dual = volmesh_dual_network(volmesh)
    #     for vkey in xyz:
    #         dual.vertex_update_xyz(vkey, xyz[vkey], constrained=False)

    #     volmesh_reciprocate(volmesh,
    #                         formdiagram,
    #                         weight=1,
    #                         min_edge=5,
    #                         max_edge=15,
    #                         fix_vkeys=xyz.keys(),)

    # dual.draw()

    volmesh.clear()
    volmesh.draw()

    return volmesh




# def cell_face_pull_interactive(volmesh):

#     hfkey = _cell_select_halfface(volmesh)

#     _cell_split_indet_vertices(volmesh, hfkey)

#     volmesh.clear()

#     # --------------------------------------------------------------------------
#     #  get edgees
#     # --------------------------------------------------------------------------
#     hf_vkeys  = volmesh.halfface_vertices(hfkey)
#     edges = {}
#     for u in hf_vkeys:
#         u_nbrs = volmesh.vertex_neighbours(u)
#         for v in u_nbrs:
#             if v not in hf_vkeys:
#                 edges[u] = v

#     hf_normal     = volmesh.halfface_normal(hfkey)
#     hf_center     = volmesh.halfface_center(hfkey)
#     hf_area       = volmesh.halfface_area(hfkey)
#     hf_vkeys      = volmesh.halfface_vertices(hfkey)

#     ckey = volmesh.cell.keys()[0]
#     cell_center = volmesh.cell_centroid(ckey)

#     xyz_dict = {}
#     for vkey in volmesh.vertex:
#         if vkey not in hf_vkeys:
#             xyz_dict[vkey] = volmesh.vertex_coordinates(vkey)

#     # --------------------------------------------------------------------------
#     #  dynamic draw
#     # --------------------------------------------------------------------------
#     rs.EnableRedraw(True)
#     def OnDynamicDraw(sender, e):
#         cp          = e.CurrentPoint
#         plane       = (cp, hf_normal)
#         new_pt_list = []
#         for u in hf_vkeys:
#             v     = edges[u]
#             u_xyz = volmesh.vertex_coordinates(u)
#             v_xyz = volmesh.vertex_coordinates(v)
#             line  = (u_xyz, v_xyz)
#             it    = intersection_line_plane(line, plane)
#             xyz_dict[u] = it
#             new_pt_list.append(it)
#             e.Display.DrawDottedLine(
#                 Point3d(*u_xyz),
#                 Point3d(*it),
#                 feedback_color)

#         for vkey in volmesh.vertex:
#             xyz = volmesh.vertex_coordinates(vkey)
#             e.Display.DrawPoint(Point3d(*xyz), 0, 6, black)

#         # old normal and area --------------------------------------------------
#         e.Display.DrawDot(
#             Point3d(*hf_center), str(round(hf_area, 3)), gray, white)

#         # draw original face ---------------------------------------------------
#         for i in range(-1, len(hf_vkeys) - 1):
#             vkey1 = hf_vkeys[i]
#             vkey2 = hf_vkeys[i + 1]
#             sp    = Point3d(*volmesh.vertex_coordinates(vkey1))
#             np    = Point3d(*volmesh.vertex_coordinates(vkey2))
#             e.Display.DrawDottedLine(sp, np, feedback_color)

#         # get current face info ------------------------------------------------
#         areas = {}
#         normals = {}
#         for fkey in volmesh.halfface:
#             face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
#             area          = area_polygon_general(face_coordinates)
#             areas[fkey]   = area
#             normal        = normal_polygon_general(face_coordinates)
#             normals[fkey] = normal

#         # draw new face areas / vectors ----------------------------------------
#         for fkey in volmesh.halfface:
#             area   = areas[fkey]
#             normal = normals[fkey]
#             value  = area / max(areas.values())
#             color  = i_to_rgb(value)
#             color  = System.Drawing.Color.FromArgb(*color)
#             scale  = 0.25
#             sp = Point3d(*cell_center)
#             ep = Point3d(*add_vectors(cell_center, scale_vector(normal, area * scale)))
#             e.Display.DrawArrow(Line(sp, ep), color, 20, 0)

#             face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
#             face_coordinates.append(face_coordinates[0])
#             polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
#             e.Display.DrawPolyline(polygon_xyz, black, 2)
#             if fkey == hfkey:
#                 xyz = centroid_polyhedron(face_coordinates)
#                 e.Display.DrawDot(Point3d(*xyz), str(round(area, 3)), black, white)
#                 e.Display.DrawPolyline(polygon_xyz, black, 6)
#                 e.Display.DrawPolygon(polygon_xyz, color, filled=True)

#     # --------------------------------------------------------------------------
#     #  input point
#     # --------------------------------------------------------------------------
#     ip   = Point3d(*hf_center)
#     line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
#     gp   = _get_target_point(line, OnDynamicDraw)

#     # --------------------------------------------------------------------------
#     #  update volmesh coordinates
#     # --------------------------------------------------------------------------
#     final_plane = (gp, hf_normal)
#     for u in edges:
#         v     = edges[u]
#         u_xyz = volmesh.vertex_coordinates(u)
#         v_xyz = volmesh.vertex_coordinates(v)
#         line  = (u_xyz, v_xyz)
#         it    = intersection_line_plane(line, final_plane)
#         volmesh.vertex_update_xyz(u, it, constrained=False)

#     volmesh.draw()


# def _cell_select_halfface(volmesh):
#     if len(volmesh.cell) > 1:
#         print("too many cells in this volmesh!")
#         return
#     hfkey = volmesh_select_face(volmesh)
#     return hfkey


# def _cell_split_indet_vertices(volmesh, hfkey):
#     ckey          = volmesh.cell.keys()[0]
#     egi           = volmesh.c_data[ckey]['egi']
#     hf_vkeys      = volmesh.halfface_vertices(hfkey)
#     egi_nbr_vkeys = egi.vertex_neighbours(hfkey)
#     for egi_fkey in hf_vkeys:
#         hfkeys = egi.face[egi_fkey]
#         n      = hfkeys.index(hfkey)
#         hfkeys = hfkeys[n:] + hfkeys[:n]
#         egi_face_vertices = [key for key in hfkeys if key not in egi_nbr_vkeys + [hfkey]]
#         fkey    = egi_fkey
#         x, y, z = volmesh.vertex_coordinates(egi_fkey)
#         for vkey in egi_face_vertices:
#             f, g = egi.mesh_split_face(fkey, hfkey, vkey)
#             volmesh.add_vertex(key=f, x=x, y=y, z=z)
#             volmesh.add_vertex(key=g, x=x, y=y, z=z)
#             for new_hfkey in hfkeys:
#                 new_vkeys = egi.vertex_faces(new_hfkey, ordered=True)
#                 volmesh.add_halfface(new_vkeys[::-1], fkey=new_hfkey)
#             volmesh.cell_vertex_delete(fkey)
#             fkey = g
#     return volmesh









# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _volmesh_compute_dependent_face_intersections(volmesh,
                                                  hfkey,
                                                  xyz,
                                                  normal=None):


    if not normal:
        normal = None

    vertex_xyz = _cell_update_halfface(volmesh, hfkey, xyz, normal)

    ckey       = volmesh.halfface_cell(hfkey)
    hf_edges   = volmesh.halfface_edges(hfkey)
    dep_hfkeys = volmesh.halfface_dependent_halffaces(hfkey)
    hf_centers = {}
    for nbr_hfkey in dep_hfkeys:
        center_key = dep_hfkeys[nbr_hfkey]
        center_xyz = vertex_xyz[center_key]
        hf_centers[nbr_hfkey] = center_xyz

    dependents = set(volmesh.halfface_dependent_halffaces(hfkey).keys())
    seen = set()

    i = 0
    while True:
        if i == 100:
            break
        if i != 0 and len(seen) == 0:
            break

        temp = []

        for d_hfkey in dependents:
            if d_hfkey not in seen:

                # compute new cell for the d_hfkey
                center = hf_centers[d_hfkey]
                next_xyz = _cell_update_halfface(volmesh,
                                                 d_hfkey,
                                                 center,
                                                 normal)
                for vkey in next_xyz:
                    if vkey not in vertex_xyz:
                        vertex_xyz[vkey] = next_xyz[vkey]

                next_d_hfkeys = volmesh.halfface_dependent_halffaces(d_hfkey)
                for fkey in next_d_hfkeys:
                    if fkey not in hf_centers:
                        center_key = next_d_hfkeys[fkey]
                        center_xyz = vertex_xyz[center_key]
                        hf_centers[fkey] = center_xyz

                temp += next_d_hfkeys.keys()

                seen.add(d_hfkey)

        dependents.update(temp)
        i += 1

    if hfkey in dependents:
        dependents.remove(hfkey)

    return vertex_xyz


def _cell_update_halfface(volmesh,
                          hfkey,
                          xyz,
                          normal=None):

    new_cell_xyz = {}

    ckey         = volmesh.halfface_cell(hfkey)
    cell_vkeys   = volmesh.cell_vertices(ckey)
    hf_vkeys     = volmesh.halfface_vertices(hfkey)
    if not normal:
        normal = volmesh.halfface_normal(hfkey)
    plane    = (xyz, normal)

    edges = {key: [] for key in hf_vkeys}
    for u in hf_vkeys:
        nbrs = volmesh.vertex_neighbours(u)
        for v in nbrs:
            if v not in hf_vkeys and v in cell_vkeys:
                edges[u].append(v)

    for u in hf_vkeys:
        v     = edges[u][0]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, plane)
        new_cell_xyz[u] = it

    return new_cell_xyz


def _volmesh_current_halfface_normals(volmesh):
    normals = {}
    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_normal(hfkey)
        normals[hfkey] = normal
    return normals


def _volmesh_current_halfface_centers(volmesh):
    centers = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        centers[hfkey] = center
    return centers


def _halffaces_avg_normals(volmesh, hfkeys):
    vectors = []
    for hfkey in hfkeys:
        vectors.append(volmesh.halfface_normal(hfkey))
    return normalize_vector(centroid_points(vectors))


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   rhino
#
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
    else:
        gp.Constrain(constraint, option)
    gp.DynamicDraw += OnDynamicDraw
    gp.Get()
    gp = gp.Point()
    return gp
