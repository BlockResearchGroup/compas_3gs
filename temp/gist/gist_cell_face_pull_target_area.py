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

from compas.geometry import scale_vector
from compas.geometry import center_of_mass_polygon
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point

from compas.utilities import i_to_rgb

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_face

from compas_3gs.helpers import polygon_normal_oriented
from compas_3gs.helpers import polygon_area_oriented


from compas_rhino.utilities import draw_labels

from compas_rhino.conduits.edges import LinesConduit


find_object    = sc.doc.Objects.Find
feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color    = System.Drawing.Color.FromArgb(255, 0, 79)
jl_blue        = System.Drawing.Color.FromArgb(0, 113, 188)
black          = System.Drawing.Color.FromArgb(0, 0, 0)
gray           = System.Drawing.Color.FromArgb(200, 200, 200)
green          = System.Drawing.Color.FromArgb(0, 255, 0)
white          = System.Drawing.Color.FromArgb(255, 255, 255)

__author__     = ['Juney Lee']
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


def cell_face_pull_target_area(volmesh, tol=1e-5):

    # pick face ----------------------------------------------------------------
    hfkey = _cell_select_halfface(volmesh)

    hf_center     = volmesh.halfface_center(hfkey)
    hf_normal     = volmesh.halfface_oriented_normal(hfkey)
    hf_area       = volmesh.halfface_oriented_area(hfkey)

    rs.AddPoint(hf_center)

    draw_labels([{
        'pos'  : hf_center,
        'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
        'color': (0, 0, 0),
        'text' : str(round(hf_area, 3))}])

    # get number ---------------------------------------------------------------
    gn = Rhino.Input.Custom.GetNumber()
    gn.SetCommandPrompt('enter target area')
    if gn.Get() != Rhino.Input.GetResult.Number:
        return None
    target = gn.Number()
    gn.Dispose()

    sign = 1
    if target - hf_area < 0:
        sign = -1

    # start --------------------------------------------------------------------
    _cell_split_indet_vertices(volmesh, hfkey)
    move_dir = _get_move_direction(volmesh, hfkey) * sign

    gr = (math.sqrt(5) + 1) / 2
    a  = 0
    b  = 20
    c  = b - (b - a) / gr
    d  = a + (b - a) / gr

    iteration = 0
    count     = 50

    labels = []

    while abs(c - d) > tol:

        if count == 0:
            break

        move_c = c * move_dir
        move_d = d * move_dir
        center_c = add_vectors(hf_center, scale_vector(hf_normal, move_c))
        center_d = add_vectors(hf_center, scale_vector(hf_normal, move_d))
        area_c = _evaluate_trial_face_area(volmesh, hfkey, center_c)
        area_d = _evaluate_trial_face_area(volmesh, hfkey, center_d)
        eval_c = target - area_c
        eval_d = target - area_d

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

        if iteration == 0:
            rs.AddPoint(center_c)
            rs.AddArcPtTanPt(hf_center, (0, 1, 0), center_d)
        rs.AddArcPtTanPt(center_c, (0, 1, 0), center_d)

        if abs(eval_c) < abs(eval_d):
            b = d
            labels.append({
                'pos'  : center_c,
                'name' : '{}.vertex.label.*'.format(volmesh.attributes['name']),
                'color': (col_c, col_c, col_c),
                'text' : str(area_c)})
        else:

            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

        print(iteration, '----------------------------------------------------')
        print(_evaluate_trial_face_area(volmesh, hfkey, center_c))
        print(_evaluate_trial_face_area(volmesh, hfkey, center_d))

        iteration += 1
        count -= 1

    final = (b + a) / 2
    translation = final * move_dir

    new_center = add_vectors(hf_center, scale_vector(hf_normal, translation))
    print(new_center)
    cell_face_pull_location(volmesh, hfkey, new_center)

    volmesh.draw()

    draw_labels(labels)

    return volmesh


def cell_face_pull_location(volmesh, hfkey, new_center):

    hf_vkeys  = volmesh.halfface_vertices(hfkey)
    edges = {}
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
    return polygon_area_oriented(new_pt_list)


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
    return move_dir


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
