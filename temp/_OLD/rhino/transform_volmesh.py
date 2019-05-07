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
from compas.geometry import centroid_polyhedron
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point

from compas_3gs.rhino import vertex_move

from compas.utilities import i_to_rgb

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector
from compas_3gs.rhino.selectors import CellSelector

from compas_rhino.helpers.volmesh import volmesh_select_vertex
from compas_rhino.helpers.volmesh import volmesh_select_vertices
from compas_rhino.helpers.volmesh import volmesh_select_face

from compas_3gs_rhino.control import VolmeshHalffaceInspector
from compas_3gs_rhino.control import VolmeshCellInspector

from compas_3gs.algorithms.planarisation import volmesh_planarise_faces


# from compas_rhino.conduits import LinesConduit

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
    #     normal = volmesh.halfface_oriented_normal(hfkey)
    #     targets[hfkey] = normal

    # vertex_move(volmesh)

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
    print('cell_hfkeys', cell_hfkeys)
    halfface_inspector = VolmeshHalffaceInspector(volmesh,
                                                  hfkeys=cell_hfkeys,
                                                  dependents=True)
    halfface_inspector.enable()

    hfkey = volmesh_select_face(volmesh)

    halfface_inspector.disable()
    del halfface_inspector



    print(hfkey)
    dep_hfkeys = volmesh.volmesh_all_dependent_halffaces(hfkey)
    print('dep_fkeys', dep_hfkeys)
    volmesh.clear()
    # volmesh.draw_edges()
    volmesh.draw_faces()

    rs.EnableRedraw(True)

    # determine here the dependent and free faces...



















    # 3. move face -------------------------------------------------------------
    hf_vkeys    = volmesh.halfface_vertices(hfkey)
    hf_normal   = volmesh.halfface_oriented_normal(hfkey)
    hf_center   = volmesh.halfface_center(hfkey)
    hf_area     = volmesh.halfface_oriented_area(hfkey)

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


        # new_pt_list = []
        # for u in hf_vkeys:
        #     v     = edges[u]
        #     u_xyz = volmesh.vertex_coordinates(u)
        #     v_xyz = volmesh.vertex_coordinates(v)
        #     line  = (u_xyz, v_xyz)
        #     it    = intersection_line_plane(line, plane)
        #     xyz_dict[u] = it
        #     new_pt_list.append(it)
        #     e.Display.DrawDottedLine(
        #         Point3d(*u_xyz),
        #         Point3d(*it),
        #         feedback_color)

        # face_coordinates = [xyz_dict[vkey] for vkey in hf_vkeys]
        # face_coordinates.append(face_coordinates[0])
        # polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
        # e.Display.DrawPolyline(polygon_xyz, black, 4)




        xyz = _volmesh_compute_dependent_face_intersections(volmesh, hfkey, cp)













        seen = set()
        for face_key in dep_hfkeys + [hfkey]:
            hf_edges   = volmesh.halfface_halfedges(face_key)
            for edge in hf_edges:
                u = edge[0]
                v = edge[1]
                pair = frozenset([u, v])
                if pair not in seen:
                    init_u = volmesh.vertex_coordinates(u)
                    init_u_xyz = Point3d(*init_u)
                    u_xyz = Point3d(*xyz[u])
                    v_xyz = Point3d(*xyz[v])
                    e.Display.DrawLine(Line(u_xyz, v_xyz), white, 5)
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
                e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)






    # --------------------------------------------------------------------------
    #  input point
    # --------------------------------------------------------------------------
    ip   = Point3d(*hf_center)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*hf_normal))
    gp   = _get_target_point(line, OnDynamicDraw)


    new_xyz = _volmesh_compute_dependent_face_intersections(volmesh, hfkey, gp)


    for key in new_xyz:
        coordinates = new_xyz[key]
        volmesh.vertex_update_xyz(key, coordinates, constrained=False)



    # target_normals = _volmesh_current_halfface_oriented_normals(volmesh)
    # target_centers = _volmesh_current_halfface_centers(volmesh)
    # for dep_hfkey in dep_hfkeys:
    #     del target_centers[dep_hfkey]
    #     pair = volmesh.halfface_opposite_halfface(dep_hfkey)
    #     if pair:
    #         del target_centers[volmesh.halfface_opposite_halfface(dep_hfkey)]

    # target_centers[hfkey] = gp
    # target_centers[volmesh.halfface_opposite_halfface(hfkey)] = gp

    # volmesh_planarise_faces(volmesh,
    #                         count=1000,
    #                         target_normals=target_normals,
    #                         target_centers=target_centers,
    #                         conduit=True)

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

    volmesh.draw()







def _cell_update_halfface(volmesh, hfkey, xyz):

    new_cell_xyz = {}

    ckey     = volmesh.halfface_cell(hfkey)
    cell_vkeys = volmesh.cell_vertices(ckey)
    hf_vkeys = volmesh.halfface_vertices(hfkey)
    plane    = (xyz, volmesh.halfface_oriented_normal(hfkey))

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





def _volmesh_compute_dependent_face_intersections(volmesh, hfkey, xyz):

    vertex_xyz = _cell_update_halfface(volmesh, hfkey, xyz)

    ckey       = volmesh.halfface_cell(hfkey)
    hf_edges   = volmesh.halfface_halfedges(hfkey)
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
                next_xyz = _cell_update_halfface(volmesh, d_hfkey, center)
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


def _volmesh_current_halfface_oriented_normals(volmesh):
    normals = {}
    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_oriented_normal(hfkey)
        normals[hfkey] = normal
    return normals


def _volmesh_current_halfface_centers(volmesh):
    centers = {}
    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        centers[hfkey] = center
    return centers


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