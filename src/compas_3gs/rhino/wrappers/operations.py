from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import intersection_line_plane
from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.utilities import i_to_rgb

from compas_rhino.helpers import volmesh_select_vertex
from compas_rhino.helpers import volmesh_select_vertices
from compas_rhino.helpers import volmesh_select_face

from compas_3gs.operations import volmesh_vertex_merge
from compas_3gs.operations import volmesh_vertex_lift
from compas_3gs.operations import volmesh_halfface_pinch
from compas_3gs.operations import volmesh_merge_adjacent_halffaces
from compas_3gs.operations import volmesh_cell_subdivide_barycentric

from compas_3gs.rhino import select_boundary_halffaces
from compas_3gs.rhino import CellSelector
from compas_3gs.rhino import VolmeshHalffaceInspector
from compas_3gs.rhino import VolmeshCellInspector

from compas_3gs.rhino import get_target_point


try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    from System.Drawing.Color import FromArgb

    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Vector3d
    from Rhino.Geometry import Line

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


__all__ = ['rhino_volmesh_vertex_lift',
           'rhino_volmesh_vertex_merge',

           'rhino_volmesh_halfface_pinch',
           'rhino_volmesh_merge_adjacent_halffaces',

           'rhino_volmesh_cell_subdivide_barycentric',
           'rhino_volmesh_pull_faces']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   vertex operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_volmesh_vertex_lift(volmesh):
    """Rhino wrapper for the vertex lift operation.
    """

    volmesh.draw()

    vkey = volmesh_select_vertex(volmesh)

    vertex_hfkeys = []
    for hfkey in volmesh.vertex_halffaces(vkey):
        if volmesh.is_halfface_on_boundary(hfkey):
            vertex_hfkeys.append(hfkey)

    xyz    = volmesh.vertex_coordinates(vkey)
    normal = volmesh.vertex_normal(vkey)

    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        for hfkey in vertex_hfkeys:
            for vkey in volmesh.halfface_vertices(hfkey):
                sp = volmesh.vertex_coordinates(vkey)
                e.Display.DrawLine(Point3d(*sp), cp, white, 2)

    ip   = Point3d(*xyz)
    axis = Rhino.Geometry.Line(ip, ip + Vector3d(*normal))
    gp   = get_target_point(axis, OnDynamicDraw)

    volmesh_vertex_lift(volmesh, vkey, gp, vertex_hfkeys)

    volmesh.draw()


def rhino_volmesh_vertex_merge(volmesh):
    """Rhino wrapper for the vertex merge operation.
    """

    volmesh.draw()

    keys = volmesh_select_vertices(volmesh)
    xyz  = centroid_points([volmesh.vertex_coordinates(key) for key in keys])

    volmesh_vertex_merge(volmesh, keys, xyz)

    volmesh.draw()


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   face operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_volmesh_halfface_pinch(volmesh):
    hfkeys = select_boundary_halffaces(volmesh)

    key = hfkeys[0]

    center = volmesh.halfface_center(key)
    normal = volmesh.halfface_oriented_normal(key)
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
            hf_normal = volmesh.halfface_oriented_normal(hfkey)
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
    gp    = get_target_point(axis, OnDynamicDraw)

    plane = (gp, normal)
    it    = intersection_line_plane(line, plane)

    translation = subtract_vectors(it, center)
    dot = dot_vectors(normal, translation)
    dot = dot / abs(dot)

    rise  = distance_point_point(center, it) * dot

    for hfkey in hfkeys:
        hf_center = volmesh.halfface_center(hfkey)
        hf_normal = volmesh.halfface_oriented_normal(hfkey)
        ep = add_vectors(hf_center, scale_vector(hf_normal, rise))

        volmesh_halfface_pinch(volmesh, hfkey, ep)

    volmesh.draw()

    return volmesh


def rhino_volmesh_merge_adjacent_halffaces(volmesh):
    volmesh.draw()
    hfkeys = select_boundary_halffaces(volmesh)
    volmesh_merge_adjacent_halffaces(volmesh, hfkeys)
    volmesh.draw()
    return volmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def rhino_volmesh_cell_subdivide_barycentric(volmesh, formdiagram=None):

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
        volmesh_cell_subdivide_barycentric(volmesh, ckey)

    volmesh.clear()
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


def rhino_volmesh_pull_faces(volmesh, uniform=False):

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
    gp   = get_target_point(line, OnDynamicDraw)

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


def _volmesh_compute_dependent_face_intersections(volmesh,
                                                  hfkey,
                                                  xyz,
                                                  normal=None):

    if not normal:
        normal = None

    vertex_xyz = _cell_update_halfface(volmesh, hfkey, xyz, normal)

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
        normal = volmesh.halfface_oriented_normal(hfkey)
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


def _halffaces_avg_normals(volmesh, hfkeys):
    vectors = []
    for hfkey in hfkeys:
        vectors.append(volmesh.halfface_oriented_normal(hfkey))
    return normalize_vector(centroid_points(vectors))


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
