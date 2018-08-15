import System.Drawing.Color
from System.Drawing.Color import FromArgb
import scriptcontext as sc

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

from compas_3gs.algorithms import volmesh_planarise_faces

from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import center_of_mass_polygon
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point

from compas_3gs.rhino import volmesh_vertex_move

from compas.utilities import i_to_rgb

from compas_rhino.helpers.selectors import VertexSelector
from compas_rhino.helpers.selectors import EdgeSelector
from compas_rhino.helpers.selectors import FaceSelector
from compas_3gs.rhino.selectors import CellSelector

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_face

from compas_3gs.rhino import VolmeshHalffaceInspector
from compas_3gs.rhino import VolmeshCellInspector

from compas_3gs.rhino.helpers import volmesh_select_dependent_halffaces


# from compas_rhino.conduits.edges import LinesConduit

import Rhino
from Rhino.Geometry import Point3d
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Line

find_object    = sc.doc.Objects.Find
feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color    = System.Drawing.Color.FromArgb(255, 0, 79)
jl_blue        = System.Drawing.Color.FromArgb(0, 113, 188)
black          = System.Drawing.Color.FromArgb(0, 0, 0)
gray           = System.Drawing.Color.FromArgb(200, 200, 200)
green          = System.Drawing.Color.FromArgb(0, 255, 0)
white          = System.Drawing.Color.FromArgb(255, 255, 255)


def volmesh_pull_faces(volmesh):

    # targets = {}

    # for hfkey in volmesh.faces():
    #     normal = volmesh.halfface_normal(hfkey)
    #     targets[hfkey] = normal

    # volmesh_vertex_move(volmesh)

    # print('test')
    # print(targets)

    # volmesh_planarise_faces(volmesh, count=5000, target_normals=targets, conduit=False)


    cell_colors = {}
    ckeys = volmesh.cell.keys()
    for index, ckey in enumerate(ckeys):
        value  = float(index) / (len(ckeys) - 1)

        color  = i_to_rgb(value)
        # color  = System.Drawing.Color.FromArgb(*color)
        cell_colors[ckey] = color
    print(cell_colors)


    # 1. pick cell -------------------------------------------------------------

    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces()
    volmesh.draw_cell_labels(color_dict=cell_colors)
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
    print('cell_hfkeys', cell_hfkeys)
    halfface_inspector = VolmeshHalffaceInspector(volmesh,
                                                  hfkeys=cell_hfkeys,
                                                  dependents=True)
    halfface_inspector.enable()

    hfkey = volmesh_select_face(volmesh)

    halfface_inspector.disable()
    del halfface_inspector



    print(hfkey)
    dep_hfkeys = volmesh_select_dependent_halffaces(volmesh, hfkey)
    print('dep_fkeys', dep_hfkeys)
    volmesh.clear()
    volmesh.draw_edges()
    volmesh.draw_faces(fkeys=dep_hfkeys)

    rs.EnableRedraw(True)

    # determine here the dependent and free faces...



















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

        # for vkey in volmesh.vertex:
        #     xyz = volmesh.vertex_coordinates(vkey)
        #     e.Display.DrawPoint(Point3d(*xyz), 0, 6, black)


        # # draw original face ---------------------------------------------------
        # for i in range(-1, len(hf_vkeys) - 1):
        #     vkey1 = hf_vkeys[i]
        #     vkey2 = hf_vkeys[i + 1]
        #     sp    = Point3d(*volmesh.vertex_coordinates(vkey1))
        #     np    = Point3d(*volmesh.vertex_coordinates(vkey2))
        #     e.Display.DrawDottedLine(sp, np, feedback_color)

        # # get current face info ------------------------------------------------
        # areas = {}
        # normals = {}
        # for fkey in volmesh.halfface:
        #     face_coordinates = [xyz_dict[vkey] for vkey in volmesh.halfface[fkey]]
        #     area          = area_polygon_general(face_coordinates)
        #     areas[fkey]   = area
        #     normal        = normal_polygon_general(face_coordinates)
        #     normals[fkey] = normal


        face_coordinates = [xyz_dict[vkey] for vkey in hf_vkeys]
        face_coordinates.append(face_coordinates[0])
        polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
        e.Display.DrawPolyline(polygon_xyz, black, 4)

    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*hf_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
    gp   = _get_target_point(line, OnDynamicDraw)

    # # --------------------------------------------------------------------------
    # #  update volmesh coordinates
    # # --------------------------------------------------------------------------
    # final_plane = (gp, hf_normal)
    # for u in edges:
    #     v     = edges[u]
    #     u_xyz = volmesh.vertex_coordinates(u)
    #     v_xyz = volmesh.vertex_coordinates(v)
    #     line  = (u_xyz, v_xyz)
    #     it    = intersection_line_plane(line, final_plane)
    #     volmesh.vertex_update_xyz(u, it, constrained=False)

    # volmesh.draw()




















def volmesh_store_initial_normals(volmesh):
    normals = {}
    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_normal(hfkey)
        normals[hfkey] = normal
    return normals



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