import scriptcontext as sc
import rhinoscriptsyntax as rs
import scriptcontext as sc

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector

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
    guid = add_arc(arc)

    # if guid:
    #     obj = find_object(guid)

    #     attr = obj.Attributes

    #     if layer:
    #         index = find_layer_by_fullpath(layer, True)
    #         if index >= 0:
    #             attr.LayerIndex = index

    #     attr.Name = name
    #     obj.CommitChanges()
    #     print(guid)

    return guid
