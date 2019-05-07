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
from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import centroid_polyhedron
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point

from compas.utilities import i_to_rgb

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_face

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented

from compas_rhino.utilities import draw_lines
from compas_rhino.utilities import draw_labels

from compas_rhino.conduits import LinesConduit


find_object    = sc.doc.Objects.Find
feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color    = System.Drawing.Color.FromArgb(255, 0, 79)
jl_blue        = System.Drawing.Color.FromArgb(0, 113, 188)
black          = System.Drawing.Color.FromArgb(0, 0, 0)
gray           = System.Drawing.Color.FromArgb(200, 200, 200)
green          = System.Drawing.Color.FromArgb(0, 255, 0)
white          = System.Drawing.Color.FromArgb(255, 255, 255)

__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
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


def cell_face_pull_target_area_direct(volmesh, tol=1e-6):

    # pick face ----------------------------------------------------------------
    hfkey = _cell_select_halfface(volmesh)

    hf_center     = volmesh.halfface_center(hfkey)
    hf_normal     = volmesh.halfface_oriented_normal(hfkey)
    hf_area       = volmesh.halfface_oriented_area(hfkey)

    rs.AddPoint(hf_center)


    # display current area -----------------------------------------------------
    draw_labels([{
        'pos'  : hf_center,
        'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
        'color': (0, 0, 0),
        'text' : str(round(hf_area, 3))}])


    # enter target area --------------------------------------------------------
    gn = Rhino.Input.Custom.GetNumber()
    gn.SetCommandPrompt('enter target area')
    if gn.Get() != Rhino.Input.GetResult.Number:
        return None
    target = gn.Number()
    gn.Dispose()


    # prep cell ----------------------------------------------------------------
    _cell_split_indet_vertices(volmesh, hfkey)


    print('hf_normal', hf_normal)

    new_xyz    = add_vectors(hf_center, hf_normal)
    trial_area = _evaluate_trial_face_area(volmesh, hfkey, new_xyz)



    ratio      = trial_area - hf_area
    print('trial_area', trial_area)
    print('ratio', ratio)

    x          = (target - hf_area) / ratio


    # new_center = add_vectors(hf_center, scale_vector(hf_normal, x))
    # _cell_face_pull_location(volmesh, hfkey, new_center)


    deviation = 1
    iteration = 0
    while deviation > tol:
        if iteration > 100:
            break




        new_center = add_vectors(hf_center, scale_vector(hf_normal, x))

        current_area = _evaluate_trial_face_area(volmesh, hfkey, new_center)


        # new_xyz = add_vectors(hf_center, hf_normal)

        # trial_area = _evaluate_trial_face_area(volmesh, hfkey, new_xyz)
        extra = (target - current_area) / ratio
        x = x + extra

        deviation = abs(target - current_area)


        iteration +=1
        print(iteration)
        print(current_area)


    y = (0, 1, 0)

    center = (0, 0, new_center[2])

    move = add_vectors(center, scale_vector(y, current_area))






    draw_lines([{
        'start': center,
        'end'  : move,
        # 'arrow': 'end',
        'layer': 'area_lines',
        'name' : 'area-{}'.format(current_area)}])





    # print(iteration)
    # print(volmesh.halfface_oriented_area(hfkey))

    _cell_face_pull_location(volmesh, hfkey, new_center)
    rs.EnableRedraw(True)

    volmesh.draw(layer='forcepolyhedra')


    return volmesh









def cell_face_pull_target_area(volmesh, tol=1e-6):

    # pick face ----------------------------------------------------------------
    hfkey = _cell_select_halfface(volmesh)

    hf_center     = volmesh.halfface_center(hfkey)
    hf_normal     = volmesh.halfface_oriented_normal(hfkey)
    hf_area       = volmesh.halfface_oriented_area(hfkey)

    rs.AddPoint(hf_center)


    # display current area -----------------------------------------------------
    draw_labels([{
        'pos'  : hf_center,
        'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
        'color': (0, 0, 0),
        'text' : str(round(hf_area, 3))}])


    # enter target area --------------------------------------------------------
    gn = Rhino.Input.Custom.GetNumber()
    gn.SetCommandPrompt('enter target area')
    if gn.Get() != Rhino.Input.GetResult.Number:
        return None
    target = gn.Number()
    gn.Dispose()


    # prep cell ----------------------------------------------------------------
    _cell_split_indet_vertices(volmesh, hfkey)


    # get move direction -------------------------------------------------------

    sign = 1  # if it needs to get larger...
    if hf_area - target > 0:
        sign = -1  # if it needs to be smaller...

    if hf_area * target < 0 :  # if it needs to flip...
        sign = -1

    move_dir = _get_move_direction(volmesh, hfkey) * sign






    rs.EnableRedraw(False)


    gr = (math.sqrt(5) + 1) / 2
    a  = 0
    b  = abs(hf_area - target)
    c  = b - (b - a) / gr
    d  = a + (b - a) / gr


    areas = []

    iteration = 0
    count     = 50


    centers = []
    labels = []

    while abs(c - d) > tol:

        if count == 0:
            break

        move_a   = a * move_dir
        move_b   = b * move_dir

        move_c   = c * move_dir
        move_d   = d * move_dir

        center_a = add_vectors(hf_center, scale_vector(hf_normal, move_a))
        center_b = add_vectors(hf_center, scale_vector(hf_normal, move_b))
        center_c = add_vectors(hf_center, scale_vector(hf_normal, move_c))
        center_d = add_vectors(hf_center, scale_vector(hf_normal, move_d))


        area_c   = _evaluate_trial_face_area(volmesh, hfkey, center_c)
        area_d   = _evaluate_trial_face_area(volmesh, hfkey, center_d)
        eval_c   = area_c - target
        eval_d   = area_d - target

        col_c = 255 - iteration * 6
        col_d = iteration * 6
        # labels.append({
        #     'pos'  : center_c,
        #     'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
        #     'color': (col_c, col_c, col_c),
        #     'text' : str(iteration)})
        # labels.append({
        #     'pos'  : center_d,
        #     'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
        #     'color': (col_d, col_d, col_d),
        #     'text' : str(iteration)})


        # if iteration == 0:
        #     rs.AddPoint(center_c)
        #     rs.AddArcPtTanPt(hf_center, (0, 1, 0), center_d)



        _cell_draw_current(volmesh, hfkey, center_c, iteration, color=(0, 0, 255))
        _cell_draw_current(volmesh, hfkey, center_d, iteration, color=(255, 0, 0))

        rs.CurrentLayer('iteration-{}'.format(iteration))
        rs.AddArcPtTanPt(center_a, (0, 1, 0), center_b)



        if abs(eval_c) < abs(eval_d):

            # rs.AddArcPtTanPt(center_c, (0, 1, 0), center_d)
            b = d

            # areas.append(area_c)


            # draw_labels([{
            #     'pos'  : center_d,
            #     'layer': 'iteration-{}'.format(iteration),
            #     'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
            #     'color': (0, 0, 255),
            #     'text' : str(area_d)}])

        else:
            # rs.AddArcPtTanPt(center_c, (0, 1, 0), center_d)
            a = c

            # rs.AddArcPtTanPt(center_c, (0, 1, 0), center_a)
            # draw_labels([{
            #     'pos'  : center_c,
            #     'layer': 'iteration-{}'.format(iteration),
            #     'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
            #     'color': (255, 0, 0),
            #     'text' : str(area_c)}])


        c = b - (b - a) / gr
        d = a + (b - a) / gr



        centers.append(center_c)


        iteration += 1
        count     -= 1


    print(areas)
    print(iteration)

    final = (b + a) / 2
    translation = final * move_dir


    # for i in range(0, len(centers) - 1):
    #     sp = centers[i]
    #     ep = centers[i + 1]
    #     rs.AddArcPtTanPt(sp, (0, 1, 0), ep)

    new_center = add_vectors(hf_center, scale_vector(hf_normal, translation))
    _cell_face_pull_location(volmesh, hfkey, new_center)

    rs.EnableRedraw(True)

    volmesh.draw(layer='forcepolyhedra')

    draw_labels(labels)

    return volmesh


def cell_face_pull_interactive(volmesh):

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

    hf_normal     = volmesh.halfface_oriented_normal(hfkey)
    hf_center     = volmesh.halfface_center(hfkey)
    hf_area       = volmesh.halfface_oriented_area(hfkey)
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
            sp    = Point3d(*volmesh.vertex_coordinates(vkey1))
            np    = Point3d(*volmesh.vertex_coordinates(vkey2))
            e.Display.DrawDottedLine(sp, np, feedback_color)

        # get current face info ------------------------------------------------
        areas = {}
        normals = {}
        for fkey in volmesh.halfface:
            face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
            area          = polygon_area_oriented(face_coordinates)
            areas[fkey]   = area
            normal        = polygon_normal_oriented(face_coordinates)
            normals[fkey] = normal

        # draw new face areas / vectors ----------------------------------------
        for fkey in volmesh.halfface:
            area   = areas[fkey]
            normal = normals[fkey]
            value  = area / max(areas.values())
            color  = i_to_rgb(value)
            color  = System.Drawing.Color.FromArgb(*color)
            scale  = 0.25
            sp = Point3d(*cell_center)
            ep = Point3d(*add_vectors(cell_center, scale_vector(normal, area * scale)))
            e.Display.DrawArrow(Line(sp, ep), color, 20, 0)

            face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
            face_coordinates.append(face_coordinates[0])
            polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
            e.Display.DrawPolyline(polygon_xyz, black, 2)
            if fkey == hfkey:
                xyz = centroid_polyhedron(face_coordinates)
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
        n      = hfkeys.index(hfkey)
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


def _cell_face_pull_location(volmesh, hfkey, new_center):

    hf_vkeys = volmesh.halfface_vertices(hfkey)
    edges    = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    plane = (new_center, volmesh.halfface_oriented_normal(hfkey))
    for u in edges:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, plane)
        volmesh.vertex_update_xyz(u, it, constrained=False)

    return volmesh


def _cell_draw_current(volmesh, hfkey, center, iteration, color):

    lines = []

    name = 'iteration-{}'.format(iteration)
    rs.AddLayer('iteration-{}'.format(iteration))



    hf_vkeys = volmesh.halfface_vertices(hfkey)
    points   = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
    normal   = polygon_normal_oriented(points)

    edges    = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v
    new_plane   = (center, volmesh.halfface_oriented_normal(hfkey))
    new_pt_list = []



    for u in hf_vkeys:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, new_plane)
        new_pt_list.append(it)


        lines.append({
            'start': u_xyz,
            'end'  : it,
            # 'arrow': 'end',
            'color': color,
            'layer': name,
            'name' : 'iteration.{}'.format(iteration)})

    new_normal = polygon_normal_oriented(new_pt_list, unitized=False)
    new_area = length_vector(new_normal)

    for i in range(-1, len(new_pt_list) - 1):
        a = new_pt_list[i]
        b = new_pt_list[i + 1]

        lines.append({
            'start': a,
            'end'  : b,
            # 'arrow': 'end',
            'color': color,
            'layer': name,
            'name' : 'iteration-{}.area-{}'.format(iteration, new_area)})

    new_normal = polygon_normal_oriented(new_pt_list, unitized=False)
    new_area = length_vector(new_normal)

    draw_lines(lines)




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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   UNUSED
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def cell_split_vertex(volmesh):

#     vkey = volmesh_select_vertex(volmesh)
#     hfkey1 = volmesh_select_face(volmesh)
#     hfkey2 = volmesh_select_face(volmesh)

#     volmesh.cell_split_vertex(vkey, hfkey1, hfkey2)
#     volmesh.draw(layer='forcepolyhedra')
#     volmesh.draw_vertexlabels()
#     volmesh.draw_facelabels()

#     ckey = volmesh.cell.keys()[0]
#     egi = volmesh.c_data[ckey]['egi']
#     egi.draw_vertexlabels(color=(255, 150, 150))
#     egi.draw()
#     egi.draw_facelabels(color=(150, 150, 150))
#