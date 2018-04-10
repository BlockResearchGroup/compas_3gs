import System.Drawing.Color
from System.Drawing.Color import FromArgb
import scriptcontext as sc
import math

import Rhino
import rhinoscriptsyntax as rs

from Rhino.Geometry import Point3d
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Line

from compas.geometry import add_vectors
from compas.geometry import area_polygon
from compas.geometry import scale_vector
from compas.geometry import normal_polygon
from compas.geometry import center_of_mass_polygon
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point

from compas.utilities import i_to_rgb

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_face

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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell transformations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

def cell_split_vertex(volmesh):

    vkey = volmesh_select_vertex(volmesh)
    hfkey1 = volmesh_select_face(volmesh)
    hfkey2 = volmesh_select_face(volmesh)

    volmesh.cell_split_vertex(vkey, hfkey1, hfkey2)
    volmesh.draw(layer='forcepolyhedra')
    volmesh.draw_vertexlabels()
    volmesh.draw_facelabels()

    ckey = volmesh.cell.keys()[0]
    egi = volmesh.c_data[ckey]['egi']
    egi.draw_vertexlabels(color=(255, 150, 150))
    egi.draw()
    egi.draw_facelabels(color=(150, 150, 150))


def cell_face_pull_target_area(volmesh, hfkey, tol=1e-5):

    if len(volmesh.cell) > 1:
        print("too many cells in this volmesh!")
        return

    hfkey = volmesh_select_face(volmesh)

    if hfkey is None:
        return

    gr = (math.sqrt(5) + 1) / 2
    a = 0
    b = distance_point_point(peak_xyz, base_xyz)
    c = b - (b - a) / gr
    d = a + (b - a) / gr

    while abs(c - d) > tol:
        move_c = c * move_dir[fkey]['dir']
        move_d = d * move_dir[fkey]['dir']
        center_c = [sum(xyz) for xyz in zip(f_center, [axis * move_c for axis in f_normal])]
        center_d = [sum(xyz) for xyz in zip(f_center, [axis * move_d for axis in f_normal])]
        eval_c = _evaluate_trial_face_area(volmesh, hfkey, center_c)
        eval_d = _evaluate_trial_face_area(volmesh, hfkey, center_d)

        if eval_c < eval_d:
            b = d
        else:
            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

    final = (b + a) / 2
    translation = final * move_dir[fkey]['dir']






def _evaluate_trial_face_area(volmesh, hfkey, new_xyz):

    hf_vkeys  = volmesh.halfface_vertices(hfkey)
    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    new_plane = (new_xyz, volmesh.halfface_normal(hfkey))

    new_pt_list = []
    for u in hf_vkeys:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, new_plane)

    return area_polygon(new_pt_list)


def _get_move_direction(volmesh, hfkey):
    move_dir = {}
    for fkey in cell.face:
        area_orig = cell.face_area(fkey)
        cell_push_face(cell, egi, fkey, 0.01)
        area_test = cell.face_area(fkey)
        if area_test > area_orig:
            move_dir[fkey] = {'fkeys_to_move'   : [fkey],
                              'dir'             : 1}
        elif area_test < area_orig:
            move_dir[fkey] = {'fkeys_to_move'   : [fkey],
                              'dir'             : -1}
        elif area_test == area_orig:
            move_dir[fkey] = {'fkeys_to_move'   : egi.vertex[fkey]['sorted_nbrs'],
                              'dir'             : 1}
    return move_dir













def cell_face_pull_location(volmesh, hfkey, new_center):

    hfkey = _cell_select_halfface(volmesh)

    _cell_split_indet_vertices(volmesh, hfkey)

    hf_vkeys  = volmesh.halfface_vertices(hfkey)
    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    plane = (new_center, volmesh.halfface_normal(hfkey))
    for u in edges:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, plane)
        volmesh.vertex_update_xyz(u, it, constrained=False)
    return volmesh












def cell_face_pull_interactive(volmesh):

    if len(volmesh.cell) > 1:
        print("too many cells in this volmesh!")
        return

    hfkey = volmesh_select_face(volmesh)


    # face info ----------------------------------------------------------------
    ckey = volmesh.cell.keys()[0]
    egi  = volmesh.c_data[ckey]['egi']

    hf_normal     = volmesh.halfface_normal(hfkey)
    hf_center     = volmesh.halfface_center(hfkey)
    hf_area       = volmesh.halfface_area(hfkey)
    hf_vkeys      = volmesh.halfface_vertices(hfkey)
    egi_nbr_vkeys = egi.vertex_neighbours(hfkey)

    # --------------------------------------------------------------------------
    #  split vertices
    # --------------------------------------------------------------------------
    for egi_fkey in hf_vkeys:
        hfkeys = egi.face[egi_fkey]
        egi_face_vertices = [key for key in hfkeys if key not in egi_nbr_vkeys + [hfkey]]
        fkey    = egi_fkey
        x, y, z = volmesh.vertex_coordinates(egi_fkey)
        for vkey in egi_face_vertices:
            f, g = egi.mesh_split_face(fkey, hfkey, vkey)
            volmesh.add_vertex(key=f, x=x, y=y, z=z)
            volmesh.add_vertex(key=g, x=x, y=y, z=z)
            for new_hfkey in hfkeys:
                new_vkeys = egi.vertex_faces(new_hfkey, ordered=True)
                volmesh.add_halfface(new_vkeys[::-1], fkey=new_hfkey)
            volmesh.cell_vertex_delete(fkey)
            fkey = g


    # --------------------------------------------------------------------------
    #  get edgees
    # --------------------------------------------------------------------------
    hf_vkeys  = volmesh.halfface_vertices(hfkey)
    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    hf_normal     = volmesh.halfface_normal(hfkey)
    hf_center     = volmesh.halfface_center(hfkey)
    hf_area       = volmesh.halfface_area(hfkey)
    hf_vkeys      = volmesh.halfface_vertices(hfkey)
    egi_nbr_vkeys = egi.vertex_neighbours(hfkey)

    # --------------------------------------------------------------------------
    #  dynamic draw
    # --------------------------------------------------------------------------
    rs.EnableRedraw(True)
    def OnDynamicDraw(sender, e):
        cp          = e.CurrentPoint
        plane       = (cp, hf_normal)
        new_pt_list = []
        for u in hf_vkeys:
            v     = edges[u]
            u_xyz = volmesh.vertex_coordinates(u)
            v_xyz = volmesh.vertex_coordinates(v)
            line  = (u_xyz, v_xyz)
            it    = intersection_line_plane(line, plane)
            new_pt_list.append(it)
            e.Display.DrawDottedLine(
                Point3d(*u_xyz),
                Point3d(*it),
                feedback_color)
            # e.Display.DrawDot(Point3d(*u_xyz), str(u), gray, white)
            # e.Display.DrawDot(Point3d(*it), str(u), black, white)

        e.Display.DrawDot(
            Point3d(*hf_center), str(round(hf_area, 3)), gray, white)
        new_center = center_of_mass_polygon(new_pt_list)
        new_area   = area_polygon(new_pt_list)
        new_normal = normal_polygon(new_pt_list)
        e.Display.DrawDot(
            Point3d(*new_center), str(round(new_area, 3)), black, white)
        pt1 = Point3d(*new_center)
        pt2 = Point3d(*add_vectors(new_center, new_normal))
        e.Display.DrawArrow(Line(pt1, pt2), green, 20, 0)

        new_pt_list.append(new_pt_list[0])
        polygon_xyz = [Point3d(*xyz) for xyz in new_pt_list]
        e.Display.DrawPolygon(polygon_xyz, jl_blue, filled=True)
        e.Display.DrawPolyline(polygon_xyz, black, 3)

        for i in range(-1, len(new_pt_list) - 1):
            sp = Point3d(*new_pt_list[i])
            np = Point3d(*new_pt_list[i + 1])
            e.Display.DrawArrow(Line(sp, np), black, 20, 0)

        # areas = [new_area]
        # faces = [new_pt_list]

        # for fkey in volmesh.halfface:
        #     if fkey != hfkey:
        #         vlist = volmesh.halfface_coorindates(fkey)
        #         vlist.append(vlist[0])
        #         faces.append(vlist)
        #         areas.append(volmesh.halfface_area(fkey))

        # print('areas', areas)
        # print('faces', faces)

        # for i in range(faces):
        #     value = areas[i] / max(areas)
        #     color = i_to_rgb(value)
        #     color = System.Drawing.Color.FromArgb(*color)
        #     polygon_xyz = [Point3d(*xyz) for xyz in faces[i]]
        #     e.Display.DrawPolyline(polygon_xyz, black, 4)
        #     e.Display.DrawPolygon(polygon_xyz, color, filled=True)


    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*hf_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
    gp   = _get_target_point(line, OnDynamicDraw)

    # --------------------------------------------------------------------------
    #  update volmesh coordinates
    # --------------------------------------------------------------------------
    final_plane = (gp, hf_normal)
    for u in edges:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, final_plane)
        volmesh.vertex_update_xyz(u, it, constrained=False)

    volmesh.draw()


def _cell_face_pull_interactive(volmesh):

    hfkey = _cell_select_halfface(volmesh)

    _cell_split_indet_vertices(volmesh, hfkey)

    volmesh.clear()

    # --------------------------------------------------------------------------
    #  get edgees
    # --------------------------------------------------------------------------
    hf_vkeys  = volmesh.halfface_vertices(hfkey)
    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    hf_normal     = volmesh.halfface_normal(hfkey)
    hf_center     = volmesh.halfface_center(hfkey)
    hf_area       = volmesh.halfface_area(hfkey)
    hf_vkeys      = volmesh.halfface_vertices(hfkey)

    ckey = volmesh.cell.keys()[0]
    cell_center = volmesh.cell_centroid(ckey)

    xyz_dict = {}
    for vkey in volmesh.vertex:
        if vkey not in hf_vkeys:
            xyz_dict[vkey] = volmesh.vertex_coordinates(vkey)

    # --------------------------------------------------------------------------
    #  dynamic draw
    # --------------------------------------------------------------------------
    rs.EnableRedraw(True)
    def OnDynamicDraw(sender, e):
        cp          = e.CurrentPoint
        plane       = (cp, hf_normal)
        new_pt_list = []
        for u in hf_vkeys:
            v     = edges[u]
            u_xyz = volmesh.vertex_coordinates(u)
            v_xyz = volmesh.vertex_coordinates(v)
            line  = (u_xyz, v_xyz)
            it    = intersection_line_plane(line, plane)
            xyz_dict[u] = it
            new_pt_list.append(it)
            e.Display.DrawDottedLine(
                Point3d(*u_xyz),
                Point3d(*it),
                feedback_color)

        for vkey in volmesh.vertex:
            xyz = volmesh.vertex_coordinates(vkey)
            e.Display.DrawPoint(Point3d(*xyz), 0, 6, black)

        # old normal and area --------------------------------------------------
        e.Display.DrawDot(
            Point3d(*hf_center), str(round(hf_area, 3)), gray, white)

        # draw original face ---------------------------------------------------
        for i in range(-1, len(hf_vkeys) - 1):
            vkey1 = hf_vkeys[i]
            vkey2 = hf_vkeys[i + 1]
            sp = Point3d(*volmesh.vertex_coordinates(vkey1))
            np = Point3d(*volmesh.vertex_coordinates(vkey2))
            e.Display.DrawDottedLine(sp, np, feedback_color)

        # get current face info ------------------------------------------------
        areas = {}
        normals = {}
        for fkey in volmesh.halfface:
            face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
            area = area_polygon(face_coordinates)
            areas[fkey] = area
            normal = normal_polygon(face_coordinates)
            normals[fkey] = normal

        # draw new face areas / vectors ----------------------------------------
        for fkey in volmesh.halfface:
            area = areas[fkey]
            normal = normals[fkey]
            value = area / max(areas.values())
            color = i_to_rgb(value)
            color = System.Drawing.Color.FromArgb(*color)
            scale = 0.25
            sp = Point3d(*cell_center)
            ep = Point3d(*add_vectors(cell_center, scale_vector(normal, area * scale)))
            e.Display.DrawArrow(Line(sp, ep), color, 20, 0)

            face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
            face_coordinates.append(face_coordinates[0])
            polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
            e.Display.DrawPolyline(polygon_xyz, black, 2)
            if fkey == hfkey:
                xyz = center_of_mass_polygon(face_coordinates)
                e.Display.DrawDot(Point3d(*xyz), str(round(area, 3)), black, white)
                e.Display.DrawPolyline(polygon_xyz, black, 6)
                e.Display.DrawPolygon(polygon_xyz, color, filled=True)

    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*hf_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
    gp   = _get_target_point(line, OnDynamicDraw)

    # --------------------------------------------------------------------------
    #  update volmesh coordinates
    # --------------------------------------------------------------------------
    final_plane = (gp, hf_normal)
    for u in edges:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, final_plane)
        volmesh.vertex_update_xyz(u, it, constrained=False)

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


def _cell_select_halfface(volmesh):

    if len(volmesh.cell) > 1:
        print("too many cells in this volmesh!")
        return

    hfkey = volmesh_select_face(volmesh)

    return hfkey


def _cell_split_indet_vertices(volmesh, hfkey):

    ckey          = volmesh.cell.keys()[0]
    egi           = volmesh.c_data[ckey]['egi']
    hf_vkeys      = volmesh.halfface_vertices(hfkey)
    egi_nbr_vkeys = egi.vertex_neighbours(hfkey)

    for egi_fkey in hf_vkeys:
        hfkeys = egi.face[egi_fkey]
        n = hfkeys.index(hfkey)
        hfkeys = hfkeys[n:] + hfkeys[:n]
        egi_face_vertices = [key for key in hfkeys if key not in egi_nbr_vkeys + [hfkey]]
        fkey    = egi_fkey
        x, y, z = volmesh.vertex_coordinates(egi_fkey)

        for vkey in egi_face_vertices:
            f, g = egi.mesh_split_face(fkey, hfkey, vkey)
            volmesh.add_vertex(key=f, x=x, y=y, z=z)
            volmesh.add_vertex(key=g, x=x, y=y, z=z)

            for new_hfkey in hfkeys:
                new_vkeys = egi.vertex_faces(new_hfkey, ordered=True)
                volmesh.add_halfface(new_vkeys[::-1], fkey=new_hfkey)

            volmesh.cell_vertex_delete(fkey)
            fkey = g

    return volmesh



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
