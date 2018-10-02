from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.geometry import add_vectors
from compas.geometry import dot_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector

from compas.utilities import i_to_rgb

from compas_3gs_rhino.display.helpers import get_index_colordict
from compas_3gs_rhino.display.helpers import get_value_colordict

from compas_rhino.utilities import xdraw_lines

try:
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

find_object = sc.doc.Objects.Find
find_layer_by_fullpath = sc.doc.Layers.FindByFullPath
add_arc = sc.doc.Objects.AddArc
add_brep     = sc.doc.Objects.AddBrep


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['draw_cell',
           'draw_cell_force_vectors',
           'draw_cell_labels',
           'clear_cell_labels',
           'draw_directed_edges_and_faces',
           'draw_network_forces',
           'draw_volmesh_face_normals',
           'draw_egi_arcs']
           # 'bake_cells_as_polysurfaces']


# ==============================================================================
#   cells
# ==============================================================================


def draw_cell(volmesh, ckey):
    hfkeys = volmesh.cell_halffaces(ckey)
    volmesh.draw_faces(fkeys=hfkeys)


def draw_cell_force_vectors(volmesh):

    ckey = volmesh.cell.keys()[0]
    center = volmesh.cell_centroid(ckey)

    lines = []
    for hfkey in volmesh.halfface:
        normal = volmesh.halfface_normal(hfkey, unitized=False)
        # normal = scale_vector(normal, -1)
        lines.append({
            'start': center,
            'end'  : add_vectors(center, normal),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name' : 'hfkey.{}'.format(hfkey)})
    xdraw_lines(lines)


def draw_cell_labels(volmesh, text=None, colors=False):

    rs.CurrentLayer(volmesh.layer)

    if colors:
        colordict = get_index_colordict(volmesh.cell)

    labels = []
    for ckey in volmesh.cell:
        color = (0, 0, 0)
        if colors:
            color = colordict[ckey]
        labels.append({
            'pos'  : volmesh.cell_center(ckey),
            'name' : '{0}.cell.label.{1}'.format(volmesh.name, ckey),
            'color': color,
            'text' : str(ckey),
        })
    return compas_rhino.xdraw_labels(labels, layer=volmesh.layer, clear=False, redraw=False)


def clear_cell_labels(volmesh, keys=None):
        if not keys:
            name = '{}.cell.label.*'.format(volmesh.name)
            guids = compas_rhino.get_objects(name=name)
        else:
            guids = []
            for key in keys:
                name = '*.cell.label.{}'.format(key)
                guid = compas_rhino.get_object(name=name)
                guids.append(guid)
        compas_rhino.delete_objects(guids)


# ==============================================================================
#   both diagrams
# ==============================================================================


def draw_directed_edges_and_faces(volmesh, network):
    volmesh.clear()
    network.clear()
    edges = []
    hfkeys = []
    for u, v in network.edges_iter():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        hfkeys.append(u_hfkey)
        edges.append({
            'start': network.vertex_coordinates(u),
            'end'  : network.vertex_coordinates(v),
            'arrow': 'end',
            'color': (0, 0, 0),
            'name' : '{}.edge.{}-{}'.format(network.name, u, v)})

    draw_volmesh_face_normals(volmesh, hfkeys)
    compas_rhino.xdraw_lines(edges, layer=network.layer, clear=False, redraw=False)
    volmesh.draw_faces(fkeys=hfkeys)
    volmesh.draw_edges()
    volmesh.draw_vertices()


def draw_network_forces(volmesh, network):
    colors = _get_force_color(volmesh, network)
    network.clear()
    network.draw_edges(color=colors)


# ==============================================================================
#   volmesh
# ==============================================================================


def draw_volmesh_face_normals(volmesh, hfkeys):
    lines = []
    for hfkey in hfkeys:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        lines.append({
            'start': center,
            'end'  : add_vectors(center, normal),
            'arrow': 'end',
            'color': (0, 255, 0),
            'name' : '{}.edge.{}'.format(volmesh.attributes['name'], hfkey)})
    compas_rhino.xdraw_lines(lines, layer=volmesh.layer, clear=False, redraw=False)


# ==============================================================================
#   network
# ==============================================================================





# ==============================================================================
#   other
# ==============================================================================


def draw_egi_arcs(egi):
    origin = egi.attributes['origin']
    rs.AddPoint(Point3d(*origin))
    rs.AddLayer('egi_arcs')
    for u, v in egi.edges():
        normal_1 = subtract_vectors(egi.vertex_coordinates(u), origin)
        normal_2 = subtract_vectors(egi.vertex_coordinates(v), origin)
        name = str(egi.edge_name(u, v))
        _draw_arc(normal_1, normal_2, origin, layer='egi_arcs', name=name)


def _draw_arc(normal_1, normal_2, origin, layer=None, name=None):
    mid_pt          = normalize_vector(add_vectors(normal_1, normal_2))
    arc             = Arc(Point3d(*[sum(axis) for axis in zip(normal_1, origin)]),
                          Point3d(*[sum(axis) for axis in zip(mid_pt, origin)]),
                          Point3d(*[sum(axis) for axis in zip(normal_2, origin)]))
    arc_as_curve    = ArcCurve(arc)
    return arc_as_curve


def bake_cells_as_polysurfaces(volmesh):
    for ckey in volmesh.cell:
        origin = volmesh.cell_centroid(ckey)
        ball   = Sphere(Point3d(*tuple(origin)), 100)
        brep   = Brep.CreateFromSphere(ball)
        rs.EnableRedraw(False)

        for hfkey in volmesh.cell_halffaces(ckey):
            center = volmesh.halfface_center(hfkey)
            normal = volmesh.halfface_normal(hfkey)
            plane  = Plane(Point3d(*tuple(center)), Vector3d(*tuple(normal)))
            intersection = brep.Trim(plane, 0.1)
            if intersection:
                brep = brep.Trim(plane, 0.001)[0]
                brep = brep.CapPlanarHoles(0.001)

        guid = add_brep(brep)
        obj = find_object(guid)
        attr = obj.Attributes
        layer = 'cells_as_polysurfaces'
        rs.AddLayer(layer)
        index = find_layer_by_fullpath(layer, True)
        if index >= 0:
            attr.LayerIndex = index
        attr.Name = 'cell.{0}'.format(ckey)
        obj.CommitChanges()


# ==============================================================================
#   helpers
# ==============================================================================


def _get_force_color(volmesh, network):
    colors = {}
    for u, v in network.edges_iter():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        face_normal   = volmesh.halfface_normal(u_hfkey)
        edge_vector   = network.edge_vector(u, v)
        dot = dot_vectors(face_normal, edge_vector)
        if dot < 0:
            value = (0, 0, 255)
        else:
            value = (255, 0, 0)
        colors[(u, v)] = value
    return colors
