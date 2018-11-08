# import time
# import rhinoscriptsyntax as rs
# import scriptcontext as sc
# import math
# from math import sin

# import compas_rhino as rhino

# from compas.datastructures.network import Network
# from compas_3gs_old.datastructures import Cell

# from compas.geometry import normalize_vector
# from compas.geometry import add_vectors
# from compas.geometry import subtract_vectors
# from compas.geometry import normal_polygon
# from compas.geometry import distance_point_point
# from compas.geometry import bestfit_plane_from_points

# from compas_rhino.helpers.network import draw_network
# from compas_rhino.helpers.mesh import display_mesh_face_labels
# from compas_rhino.helpers.mesh import select_mesh_faces

# from compas_3gs.algorithms import egi
# from compas_3gs.algorithms import arearize
# from compas_3gs.algorithms.arearization import _scale_polygon_by_area
# from compas_3gs.algorithms.arearization import _area_deficit

# from compas_3gs.utilities.drawing import draw_egi
# from compas.utilities import geometric_key

# from Rhino.Geometry import Sphere
# from Rhino.Geometry import Point3d
# from Rhino.Geometry import Vector3d
# from Rhino.Geometry import Plane
# from Rhino.Geometry import Brep

# from compas_3gs.utilities.drawing import draw_cell


# add_brep     = sc.doc.Objects.AddBrep
# find_object = sc.doc.Objects.Find


__all__ = []

# __all__ = ['_egi_spoke',
#            '_cell_as_brep',
#            '_cell_as_mesh',
#            '_arearize_gfp',
#            '_modify_face_attributes']


# def _egi_spoke():
#     rs.AddLayer('EGI')
#     rs.AddLayer('cell_unit')
#     rs.AddLayer('cell_adjusted')

#     #   make network from rhino lines ------------------------------------------
#     crvs  = rs.GetObjects("pick lines", preselect=True, filter=rs.filter.curve)
#     lines = [[rs.CurveStartPoint(crv), rs.CurveEndPoint(crv)] for crv in crvs]
#     network = Network.from_lines(lines)
#     network.set_vertices_attributes(attr_dict={'type'           : None,
#                                                'normal'         : None,
#                                                'target_area'    : None,
#                                                'fix_orientation': True,
#                                                'location'       : None,
#                                                'avg'            : False,})
#     #   sort -------------------------------------------------------------------
#     keys = []
#     for key in network.vertices():
#         if not network.is_vertex_leaf(key):
#             keys.append(key)
#     for key in keys:
#         cent = network.vertex_coordinates(key)
#         network.attributes['origin']    = cent
#         network.vertex[key]['type']     = 'origin'
#         network.vertex[key]['location'] = cent
#         nbrs = network.neighbours(key)
#         for nbr_key in nbrs:
#             nbr_xyz = network.vertex_coordinates(nbr_key)
#             dist = distance_point_point(cent, nbr_xyz)
#             vec = normalize_vector(subtract_vectors(nbr_xyz, cent))
#             x, y, z = add_vectors(cent, vec)
#             network.vertex[nbr_key]['x'] = x
#             network.vertex[nbr_key]['y'] = y
#             network.vertex[nbr_key]['z'] = z
#             network.vertex[nbr_key]['type']   = 'face'
#             network.vertex[nbr_key]['normal'] = vec
#             network.vertex[nbr_key]['location']   = add_vectors(cent, vec)
#             network.vertex[nbr_key]['target_area'] = dist
#     draw_network(network,
#                  layer='EGI')
#     return network


# def _cell_as_planes(egi):
#     cell        = Cell()
#     cell.name   = 'cell'

#     origin  = egi.attributes['origin']
#     size = Interval (-20, 20)
#     fkeys = []
#     for vkey in egi.vertex:
#         if egi.vertex[vkey]['type'] == 'face':
#             fkeys.append(vkey)
#     for key in fkeys:
#         plane   = Plane (   Point3d  (*tuple(normals[key])),
#                             Vector3d (*tuple(normals[key])) )
#         plane_srf = PlaneSurface (plane, size, size)
#         plane_brep = plane_srf.ToBrep()

#         for nbr_key in fkeys:
#             if nbr_key != key:
#                 nbr_plane = Plane ( Point3d  (*tuple(normals[nbr_key])),
#                                     Vector3d (*tuple(normals[nbr_key])) )
#                 intersection = plane_brep.Trim(nbr_plane, 0.001)
#                 if intersection:
#                     plane_brep = plane_brep.Trim(nbr_plane, 0.001)[0]

#         for loop in plane_brep.Loops:
#             face     = []
#             curve    = loop.To3dCurve()
#             segments = curve.Explode()
#             pts      = []
#             for segment in segments:
#                 pts.append(segment.PointAtStart)
#             for point in pts:
#                 pt_gkey = geometric_key(point, precision='5f')
#                 face.append(cell_v_gkeys[pt_gkey])


# def _cell_as_brep(egi):
#     origin  = egi.attributes['origin']
#     ball    = Sphere(Point3d(*tuple(origin)), 50)
#     brep = Brep.CreateFromSphere(ball)
#     face_normal_dict = {}
#     rs.EnableRedraw(False)
#     for vkey in egi.vertex:
#         if egi.vertex[vkey]['type'] == 'face':
#             print vkey
#             print egi.vertex[vkey]['location']
#             print egi.vertex[vkey]['normal']
#             print brep

#             normal = egi.vertex[vkey]['normal']
#             normal_gkey = geometric_key(normal, precision='5f')
#             face_normal_dict[normal_gkey] = vkey
#             center = egi.vertex_coordinates(vkey)
#             plane  = Plane(Point3d(*tuple(center)),
#                            Vector3d(*tuple(normal)))
#             intersection = brep.Trim(plane, 0.1)
#             if intersection:
#                 brep = brep.Trim(plane, 0.001)[0]
#                 brep = brep.CapPlanarHoles(0.001)

#             # guid = add_brep(brep)
#             # obj = find_object(guid)
#             # attr = obj.Attributes
#             # attr.Name = 'cut_by_face.{0}'.format(vkey)
#             # obj.CommitChanges()


#     return brep, face_normal_dict


# def _cell_as_mesh(egi):
#     #   make brep --------------------------------------------------------------
#     brep, face_normal_dict = _cell_as_brep(egi)
#     cell        = Cell()
#     cell.name   = 'cell'
#     cell_v_gkeys = {}

#     for vertex in brep.Vertices:
#         x, y, z = vertex.Location
#         index   = vertex.VertexIndex
#         v_gkey  = geometric_key((x, y, z), precision='5f')
#         cell_v_gkeys[v_gkey] = index
#         cell.add_vertex(x=x, y=y, z=z, key=index)
#     for loop in brep.Loops:
#         face     = []
#         curve    = loop.To3dCurve()
#         segments = curve.Explode()
#         pts      = []
#         for segment in segments:
#             pts.append(segment.PointAtStart)
#         pt_cycle = pts + [pts[0]]
#         normal   = normal_polygon(pts, unitized=True)
#         n_gkey   = geometric_key(normal, precision='5f')
#         for point in pts:
#             pt_gkey = geometric_key(point, precision='5f')
#             face.append(cell_v_gkeys[pt_gkey])

#         fkey = face_normal_dict[n_gkey]
#         cell.add_face(face, fkey=fkey)
#         cell.face_type[fkey] = egi.vertex[fkey]['type']

#     return cell, egi



# def _arearize_gfp(egi, count=50, step=0.01, threshold=0.001):

#     cell, egi = _cell_as_mesh(egi)


#     # # hexagon example 1
#     # loads = [0, 1, 4]
#     # supports = [2, 3, 5, 6, 7, 8]
#     # others = []
#     # all_faces = loads + supports + others

#     # areas = [cell.face_area(fkey) for fkey in supports]
#     # average_area = sum(areas) / len(areas)

#     # for fkey in all_faces:
#     #     if fkey in supports:
#     #         egi.vertex[fkey]['fix_orientation'] = False
#     #         # if fkey in [2, 3, 8]:
#     #         #     egi.vertex[fkey]['target_area'] = 1.5
#     #         # elif fkey in [5, 6, 7]:
#     #         #     egi.vertex[fkey]['target_area'] = 4
#     #     if fkey in others:
#     #         egi.vertex[fkey]['fix_orientation'] = False

#     # egi.vertex[2]['target_area'] = 4
#     # egi.vertex[3]['target_area'] = 4
#     # egi.vertex[8]['target_area'] = 1.5
#     # egi.vertex[5]['target_area'] = 1.5
#     # egi.vertex[6]['target_area'] = 1.5
#     # egi.vertex[7]['target_area'] = 4


#     # pentagon example 1
#     loads = [6, 2, 8]
#     supports = [3, 5]
#     others = [0, 4, 1]
#     all_faces = loads + supports + others

#     areas = [cell.face_area(fkey) for fkey in supports]
#     average_area = sum(areas) / len(areas)

#     # for fkey in all_faces:
#     #     if fkey in supports:
#     #         egi.vertex[fkey]['fix_orientation'] = False
#     #         # if fkey in [2, 3, 8]:
#     #         #     egi.vertex[fkey]['target_area'] = 1.5
#     #         # elif fkey in [5, 6, 7]:
#     #         #     egi.vertex[fkey]['target_area'] = 4
#     #     if fkey in others:
#     #         egi.vertex[fkey]['fix_orientation'] = False

#     egi.vertex[6]['target_area'] = 5
#     egi.vertex[2]['target_area'] = 5
#     egi.vertex[8]['target_area'] = 5

#     # egi.vertex[0]['target_area'] = 2.5
#     egi.vertex[3]['target_area'] = 2.5
#     # egi.vertex[1]['target_area'] = 7.5
#     # egi.vertex[4]['target_area'] = 2.5
#     egi.vertex[5]['target_area'] = 2.5





#     iteration_count = 0
#     average_area = 0




#     while count:
#         vkey = 4

#         cell, egi = _cell_as_mesh(egi)


#         new_xyz = {}

#         area_difference = dict((fkey, egi.vertex[fkey]['target_area'] - cell.face_area(fkey)) for fkey in cell.face)
#         current_areas   = dict((fkey, cell.face_area(fkey)) for fkey in cell.face)

#         if iteration_count == 0:
#             areas = [cell.face_area(fkey) for fkey in supports]
#             average_area += sum(areas) / len(areas)



#         for fkey in loads + supports:
#             center = cell.face_center(fkey)
#             delta  = area_difference[fkey]

#             target_area = egi.vertex[fkey]['target_area']
#             # if fkey in supports:
#             #     areas = [cell.face_area(fkey) for fkey in supports + others]
#             #     average_area = sum(areas) / len(areas)
#             #     target_area = average_area


#             new_face = _scale_polygon_by_area(cell, egi, fkey, target_area)
#             for vkey in new_face:
#                 if vkey not in new_xyz:
#                     new_xyz[vkey] = []
#                 new_xyz[vkey].append(new_face[vkey])

#             # if  iteration_count % 5 == 0:
#             #     rs.AddLayer('iteration.{0}'.format(iteration_count))
#             #     r = 255 - (iteration_count * 10) % 255
#             #     g = 0
#             #     b = (iteration_count * 10) % 255
#             #     f_vkeys  = cell.face_vertices(fkey, ordered=True)
#             #     polygon  = [new_face[vkey] for vkey in f_vkeys]
#             #     polyline = [{'points': polygon + [polygon[0]],
#             #                  'color': (r, g, b),}]
#             #     rhino.xdraw_polylines(polyline, layer='iteration.{0}'.format(iteration_count), clear=False, redraw=False)

#         translation = subtract_vectors(egi.attributes['origin'], cell.cell_center_of_mass())
#         for vkey in new_xyz:
#             final_xyz = [sum(axis) for axis in zip(*new_xyz[vkey])]
#             final_xyz = [xyz / len(new_xyz[vkey]) for xyz in final_xyz]

#             final_xyz = add_vectors(final_xyz, translation)
#             cell.vertex[vkey]['x'] = final_xyz[0]
#             cell.vertex[vkey]['y'] = final_xyz[1]
#             cell.vertex[vkey]['z'] = final_xyz[2]

#         draw_cell(cell,
#               layer='cell_adjusted',
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=False,
#               show_face_labels=False,
#               show_vertex_labels=False,
#               vertex_color=None,
#               edge_color=(255, 0, 0),
#               face_color=None)


#         for fkey in all_faces:
#             center  = cell.face_center(fkey)
#             # rs.AddPoint(Point3d(*tuple(center)))
#             face_normal = cell.face_normal(fkey, unitized=True)
#             egi.vertex[fkey]['location'] = center
#             # rs.AddLine((Point3d(*tuple(center))), add_vectors(center, face_normal))

#             # plane = Plane(Point3d(*tuple(center)), Vector3d(*tuple(face_normal)))
#             # rectangle = rs.AddRectangle(plane, 2, 2)
#             # rs.AddPlanarSrf(rectangle)

#             egi.vertex[fkey]['x'] = center[0]
#             egi.vertex[fkey]['y'] = center[1]
#             egi.vertex[fkey]['z'] = center[2]


#             if egi.vertex[fkey]['fix_orientation'] == False:

#                 f_vkeys      = cell.face_vertices(fkey, ordered=True)
#                 polygon      = [cell.vertex_coordinates(vkey) for vkey in f_vkeys]
#                 center, normal = bestfit_plane_from_points(polygon)
#                 egi.vertex[fkey]['normal'] = face_normal



#         # check threshold ------------------------------------------------------
#         max_diff = max([abs(area_difference[fkey]) for fkey in cell.face])
#         if max_diff < threshold:
#             break
#         sc.doc.Views.Redraw()
#         count           -= 1
#         iteration_count += 1


#     # for fkey in all_faces:
#     #     center  = cell.face_center(fkey)
#     #     face_normal = cell.face_normal(fkey, unitized=True)
#     #     egi.vertex[fkey]['location'] = center
#     #     rs.AddLine((Point3d(*tuple(center))), add_vectors(center, face_normal))

#     draw_cell(cell,
#               layer='cell_adjusted',
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=True,
#               show_face_labels=True,
#               show_vertex_labels=False,
#               vertex_color=None,
#               edge_color=(255, 0, 0),
#               face_color=None)

#     add_brep(_cell_as_brep(egi)[0])

#     return cell, egi



# def _modify_face_attributes(cell, egi):
#     display_mesh_face_labels(cell)
#     fkeys = select_mesh_faces(cell)
#     #   ask --------------------------------------------------------------------
#     options = ['fix_orientation',
#                'target_area',
#                'avg']
#     option  = rs.GetString(message='modify face attributes',
#                            strings=options)
#     # ==========================================================================
#     #   fix orientation
#     # ==========================================================================
#     if option in ('fix_orientation'):
#         new_orientation = rs.GetString(message='Fix face orientation?',
#                                        strings=['Yes', 'No'])
#         if new_orientation in ('Yes'):
#             for key in fkeys:
#                 egi.vertex[key]['fix_orientation'] = True
#         if new_orientation in ('No'):
#             for key in fkeys:
#                 egi.vertex[key]['fix_orientation'] = False
#     # ==========================================================================
#     #   new target areas
#     # ==========================================================================
#     if option in ('target_area'):
#         new_area = rs.GetReal(message='enter new value',
#                               minimum=0)
#         for key in fkeys:
#             print key, egi.vertex[key]['target_area']
#         if isinstance(new_area, float):
#             for key in fkeys:
#                 egi.vertex[key]['target_area'] = new_area
#         for key in egi.vertex:
#             print key, egi.vertex[key]['target_area']
#     # ==========================================================================
#     #   avg
#     # ==========================================================================
#     if option in ('avg'):
#         new_orientation = rs.GetString(message='average target area?',
#                                        strings=['Yes', 'No'])
#         if new_orientation in ('Yes'):
#             for key in fkeys:
#                 egi.vertex[key]['avg'] = True
#         if new_orientation in ('No'):
#             for key in fkeys:
#                 egi.vertex[key]['avg'] = False

#     draw_cell(cell,
#               layer='EGI_cell',
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=False,
#               show_face_labels=False,
#               show_vertex_labels=False,
#               vertex_color=None,
#               edge_color=None,
#               face_color=None)
#     return cell, egi
