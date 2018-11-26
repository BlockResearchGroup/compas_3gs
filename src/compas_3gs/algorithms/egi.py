
__all__ = []

# import time

# import System
# from System.Drawing import Color
# from System.Drawing.Color import FromArgb

# from compas.datastructures import Network
# # from compas.datastructures import Mesh
# from compas_3gs.datastructures import Mesh3gs as Mesh
# from compas.topology.duality import _find_first_neighbour

# from compas.geometry import distance_point_point
# from compas.geometry import centroid_polyhedron
# from compas.geometry import add_vectors
# from compas.geometry import cross_vectors
# from compas.geometry import subtract_vectors
# from compas.geometry import normalize_vector
# from compas.geometry import is_coplanar
# from compas.geometry import Vector
# from compas.geometry import add_vectors
# from compas.geometry import subtract_vectors
# from compas.geometry import scale_vector
# from compas.geometry import distance_point_point
# from compas.geometry import centroid_points
# from compas.geometry import project_points_plane
# from compas.geometry import bestfit_plane
# from compas.geometry import is_point_on_segment
# from compas.geometry import intersection_line_line
# from compas.geometry import offset_polygon
# from compas.geometry import midpoint_line

# from compas.utilities.maps import geometric_key


# try:
#     import rhinoscriptsyntax as rs
#     import scriptcontext as sc
#     import Rhino
# except ImportError:
#     compas.raise_if_ironpython()


# from Rhino.Geometry import Point3d
# from Rhino.Geometry import ArcCurve
# from Rhino.Geometry import Vector3d
# from Rhino.Geometry import Circle
# from Rhino.Geometry import Plane

# from compas_3gs_rhino.display.drawing import _draw_arc

# from Rhino.Geometry.Intersect.Intersection import CurveCurve as CCX

# from Rhino.DocObjects.ObjectColorSource import ColorFromObject
# from Rhino.DocObjects.ObjectDecoration import EndArrowhead

# from compas_rhino.helpers.network import network_draw

# import compas_rhino.utilities as rhino

# from compas_3gs.algorithms import mesh_arearisation

# from compas_3gs_rhino.display import mesh_arearisation_conduit


# add_arc      = sc.doc.Objects.AddArc
# add_brep     = sc.doc.Objects.AddBrep
# add_circle   = sc.doc.Objects.AddCircle
# add_curve    = sc.doc.Objects.AddCurve
# add_dot      = sc.doc.Objects.AddTextDot
# add_line     = sc.doc.Objects.AddLine
# add_point    = sc.doc.Objects.AddPoint
# add_polyline = sc.doc.Objects.AddPolyline
# find_object  = sc.doc.Objects.Find
# find_layer_by_fullpath = sc.doc.Layers.FindByFullPath

# __author__    = ['Juney Lee']
# __copyright__ = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
# __license__   = 'Apache License, Version 2.0'
# __email__     = ['juney@arch.ethz.ch', 'vanmelet@ethz.ch']
# __status__    = 'Development'
# __date__      = 'Mar 3, 2017'


__all__ = []


# __all__       =['create_egi',
#                 'create_unit_cell',
#                 'arearise_gfp']



# def global_force_polyhedron():

#     egi = Network()


#     vertices = {}

#     geokeys = {}
#     points  = points = rs.GetPointCoordinates(message='select points')
#     for i in range(len(points)):
#         geokeys[geometric_key(points[i])] = i

#         egi.add_vertex(x=vertex_xyz[0],
#                        y=vertex_xyz[1],
#                        z=vertex_xyz[2],
#                        key=vkey,
#                        attr_dict={'type'      : 'face',
#                                   'normal'    : None,
#                                   'magnitude' : None,
#                                   'nbrs'      : []}
#                        )



#     loads  = rs.GetObjects("pick lines", preselect=True, filter=rs.filter.curve)
#     for i in range(len(points)):
#         line        = lines[i]
#         sp          = rs.CurveStartPoint(line)
#         ep          = rs.CurveEndPoint(line)
#         mag         = rs.CurveLength(line)







# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # EGI
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************

# def arearise_gfp(cell, egi, count=500, conduit=True):

#     # flat = [1, 2, 3, 4, 5]
#     # flat = []

#     for vkey in egi.vertex:
#         if egi.vertex[vkey]['load']:
#             egi.vertex[vkey]['normal'] = (0, 0, 1)


#     # for vkey in egi.vertex:
#     #     if vkey in flat:
#     #         egi.vertex[vkey]['normal'] = (0, 0, 1)
#     #         egi.vertex[vkey]['magnitude'] = 1
#     #     elif egi.vertex[vkey]['type'] == 'face':
#     #         egi.vertex[vkey]['magnitude'] = 5
#     print('hello')
#     print('here', egi.vertex)

#     target_normals = {}
#     target_areas   = {}
#     for vkey in egi.vertex:
#         print(egi.vertex[vkey]['normal'])
#         if egi.vertex[vkey]['normal'] is not None:
#             target_normals[vkey] = egi.vertex[vkey]['normal']
#         if egi.vertex[vkey]['magnitude'] is not None:
#             target_areas[vkey] = egi.vertex[vkey]['magnitude']

#     print(target_areas)

#     if conduit:
#         conduit = mesh_arearisation_conduit(cell, target_areas)
#         conduit.Enabled = True



#     mesh_arearisation(cell,
#                       count=count,
#                       target_normals=target_normals,
#                       target_centers=None,
#                       target_areas=target_areas,
#                       fix_boundary=False,
#                       fix_all=False,
#                       omit_vkeys=[],
#                       flat_tolerance=0.0001,
#                       area_tolerance=0.0001)

#     # arearize(cell=cell, egi=egi, count=50)

#     if conduit:
#         conduit.Enabled = False
#         del conduit

#     draw_cell(cell,
#                   layer='EGI::EGI_cell',
#                   clear=False,
#                   redraw=True,
#                   show_faces=True,
#                   show_vertices=False,
#                   show_edges=True,
#                   show_face_labels=False,
#                   show_vertex_labels=False,
#                   vertex_color=None,
#                   edge_color=None,
#                   face_color=None)


# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # EGI
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def create_egi():
#     """ Sequence of functions to generate the EGI Network and the corresponding
#     dual polyhedron as Mesh.

#     """
#     # ==========================================================================
#     # 0.  Initialize
#     # ==========================================================================
#     rs.AddLayer('EGI')
#     rs.AddLayer('EGI::EGI_cell')
#     rs.AddLayer('EGI::EGI_cell_zero')
#     rs.AddLayer('EGI::EGI_vertices_face')
#     rs.AddLayer('EGI::EGI_vertices_zero')
#     rs.AddLayer('EGI::EGI_vertices_ghost')
#     rs.AddLayer('EGI::EGI_edges')
#     rs.AddLayer('EGI::EGI_arcs')

#     rs.AddLayer('triangles')
#     rs.AddLayer('offset_faces')
#     rs.AddLayer('new_cell_edges')
#     rs.AddLayer('egi_normals')
#     # ==========================================================================
#     # 3a, 3b  :   Generate EGI network
#     # ==========================================================================
#     egi_network = egi()

#     # sp = egi_network.attributes['origin']
#     # for vkey in egi_network.vertex:
#     #     ep = egi_network.vertex_coordinates(vkey)
#     #     normal = [{'start': sp,
#     #                'end'  : ep,
#     #                'name' : 'normal.vkey.{0}'.format(vkey),
#     #                'arrow' : 'end',
#     #                'color': (0,0,255),}]
#     #     rhino.xdraw_lines(normal, layer='egi_normals', clear=False, redraw=False)

#     draw_egi(egi_network,
#              as_lines=False,
#              show_faces=False,
#              show_vertices=True,
#              show_labels=False,
#              show_edges=True,
#              delete=False)


#     return egi_network



# def egi(zero_faces=False):
#     """Returns the EGI of an equilibrated system of forces as a Network.

#     Note:
#         For now, this assumes that the forces are already in equilibrium...

#     Parameters:
#         normals :   Currently, manually input as Rhino objects... eventually will
#                     come from the edges of formpolyhedra-Newtork object.
#         node    :   Currently, manually input as a Rhino point... eventually will
#                     come from formpolyhedra Newtork.vertex.

#     Returns:
#         Network :   With added vertex attributes carrying EGI information:
#                     - 'type'        : face, zero or ghost
#                     - 'normal'      : the normal of the faces
#                     - 'magnitude'   : force magnitudes, or eventual face areas
#                     - 'nbrs'        : list of nbr vkeys
#                     - 'sorted_nbrs' : sorted list of nbr_keys

#     """

#     target_normals = {}

#     # ==========================================================================
#     #   1.  Manually feed normals and origin
#     # ==========================================================================
#     lines  = rs.GetObjects("pick lines", preselect=True, filter=rs.filter.curve)
#     origin = Rhino.Input.Custom.GetPoint()
#     origin.SetCommandPrompt("pick origin")
#     origin.Get()
#     origin = origin.Point()
#     origin = [origin[0], origin[1], origin[2]]
#     rs.EnableRedraw(False)
#     # timer --------------------------------------------------------------------
#     start_time = time.time()
#     # ==========================================================================
#     #   2.  Initialize egi Network
#     # ==========================================================================
#     egi = Network()
#     egi.name                    = 'egi'
#     egi.attributes['name']      = 'egi'
#     egi.attributes['origin']    = origin
#     vertex_geokeys              = {}

#     load_number = 0
#     rxn_number = 0
#     for i in range(len(lines)):
#         line  = lines[i]
#         layer = rs.ObjectLayer(line)
#         if layer == 'load':
#             load_number += 1
#         if layer == 'rxn':
#             rxn_number += 1

#     for i in range(len(lines)):
#         vkey  = i
#         line  = lines[i]
#         layer = rs.ObjectLayer(line)
#         sp    = rs.CurveStartPoint(line)
#         ep    = rs.CurveEndPoint(line)
#         # mag   = rs.CurveLength(line)
#         mag = 4
#         if layer == 'rxn':
#             mag = 10 / rxn_number
#         if layer == 'load':
#             mag = 10 / load_number
#         normal      = normalize_vector(subtract_vectors(ep, sp))
#         vertex_xyz  = add_vectors(normal, origin)
#         vertex_geokeys[geometric_key(list(normal), precision='3f')] = vkey
#         load = False
#         if layer == 'load':
#             load = True
#         egi.add_vertex(x=vertex_xyz[0],
#                        y=vertex_xyz[1],
#                        z=vertex_xyz[2],
#                        key=vkey,
#                        attr_dict={'type'      : 'face',
#                                   'load'      : load,
#                                   'normal'    : normal,
#                                   'magnitude' : mag,
#                                   'nbrs'      : []}
#                        )
#     # ==========================================================================
#     #   3.  Draw main arcs --> identify main adjacencies
#     # ==========================================================================
#     connectivity    = {}
#     vkey_pairs_seen = set()
#     for vkey in egi.vertex:
#         connectivity[vkey]  = {}
#         v_crs_dict          = {}
#         for nbr_vkey in egi.vertex:
#             if nbr_vkey is not vkey:
#                 normal_1    = egi.vertex[vkey]['normal']
#                 normal_2    = egi.vertex[nbr_vkey]['normal']
#                 # This checks if the normals are opposite ----------------------
#                 added       = add_vectors(normal_1, normal_2)
#                 dist        = distance_point_point((0, 0, 0), added)
#                 if dist > 0.001:
#                     this_crs    = cross_vectors(normal_1, normal_2)
#                     unit_crs    = normalize_vector(this_crs)
#                     crs_gkey    = geometric_key(list(unit_crs), precision='3f')
#                     nbr_dict    = {'key'           : nbr_vkey,
#                                    'crs_product'   : this_crs}
#                     # Check to see if any other normals are coplanar -----------
#                     if crs_gkey not in v_crs_dict:
#                         v_crs_dict[crs_gkey]    = nbr_dict
#                     # If the arcs are coplanar, then choose the closer one -----
#                     elif crs_gkey in v_crs_dict:
#                         this_dist   = distance_point_point(egi.vertex_coordinates(vkey),
#                                                            egi.vertex_coordinates(nbr_vkey))
#                         test_dist   = distance_point_point(egi.vertex_coordinates(vkey),
#                                                            egi.vertex_coordinates(v_crs_dict[crs_gkey]['key']))
#                         if this_dist < test_dist:
#                             del v_crs_dict[crs_gkey]
#                             v_crs_dict[crs_gkey] = nbr_dict
#         # Add to overall connectivity dict -------------------------------------
#         for crs_gkey in v_crs_dict:
#             nbr_vkey    = v_crs_dict[crs_gkey]['key']
#             vkey_pair   = frozenset([vkey, nbr_vkey])
#             if vkey_pair not in vkey_pairs_seen:
#                 vkey_pairs_seen.add(vkey_pair)
#                 connectivity[vkey][nbr_vkey] = None
#     # Use connectivity dict to make arcs ---------------------------------------
#     arcs = {}
#     for vkey in connectivity:
#         for nbr_vkey in connectivity[vkey]:
#             normal_1 = egi.vertex[vkey]['normal']
#             normal_2 = egi.vertex[nbr_vkey]['normal']
#             arc      = _draw_arc(normal_1, normal_2, origin)
#             if len(arcs) == 0:
#                 arc_key = 0
#             else:
#                 arc_key = max(int(x) for x in arcs.keys()) + 1
#             arcs[arc_key]   = {'arc'        : arc,
#                                'vkeys'      : [vkey, nbr_vkey],
#                                'end_vkeys'  : [vkey, nbr_vkey],
#                                'int_vkeys'  : {}, }


#     # ==========================================================================
#     #   4.  Find arc intersections --> identify cross adjacencies
#     # ==========================================================================
#     if zero_faces:
#         arc_pairs_seen = set()
#         for arckey_1 in arcs:
#             for arckey_2 in arcs:
#                 if arckey_1 != arckey_2:
#                     arc_pair = frozenset([arckey_1, arckey_2])
#                     if arc_pair not in arc_pairs_seen:
#                         arc_1 = arcs[arckey_1]['arc']
#                         arc_2 = arcs[arckey_2]['arc']
#                         intersection = _curve_curve_intx(arc_1, arc_2)
#                         if intersection:
#                             new_vkey   = max(int(vkey) for vkey in egi.vertex.keys()) + 1
#                             new_normal = subtract_vectors(intersection, origin)
#                             new_normal = normalize_vector(new_normal)
#                             new_vertex_geokey = geometric_key(new_normal, precision='3f')

#                             # if intersection is not an endpoint -------------------
#                             if new_vertex_geokey not in vertex_geokeys.keys():
#                                 vertex_geokeys[new_vertex_geokey] = new_vkey
#                                 egi.add_vertex(x=intersection[0],
#                                                y=intersection[1],
#                                                z=intersection[2],
#                                                key=new_vkey,
#                                                attr_dict={'type'      : 'zero',
#                                                           'normal'    : new_normal,
#                                                           'load'      : False,
#                                                           'magnitude' : 0,
#                                                           'nbrs'      : []})
#                                 arcs[arckey_1]['vkeys'].append(new_vkey)
#                                 arcs[arckey_2]['vkeys'].append(new_vkey)
#                                 arcs[arckey_1]['int_vkeys'][new_vkey] = arckey_2
#                                 arcs[arckey_2]['int_vkeys'][new_vkey] = arckey_1

#                             # if intersection already exists -----------------------
#                             elif new_vertex_geokey in vertex_geokeys.keys():
#                                 vkey = vertex_geokeys[new_vertex_geokey]
#                                 if vkey not in arcs[arckey_1]['vkeys']:
#                                     arcs[arckey_1]['vkeys'].append(vkey)
#                                     arcs[arckey_1]['int_vkeys'][vkey] = arckey_2
#                                 if vkey not in arcs[arckey_2]['vkeys']:
#                                     arcs[arckey_2]['vkeys'].append(vkey)
#                                     arcs[arckey_2]['int_vkeys'][vkey] = arckey_1
#                             arc_pairs_seen.add(arc_pair)


#     # ==========================================================================
#     #   5.  weeding out
#     # ==========================================================================
#     new_arcs = {}
#     for arckey in arcs:
#         # print '----------------------------------------------------------'
#         # print 'arckey', arckey
#         # print 'end_vkeys', arcs[arckey]['end_vkeys']
#         # print 'int_vkeys', arcs[arckey]['int_vkeys'].keys()
#         # print len(arcs[arckey]['int_vkeys'].keys())

#         # if len(arcs[arckey]['int_vkeys'].keys()) > 1:
#         #     all_pt = arcs[arckey]['end_vkeys']
#         #     for vkey in arcs[arckey]['int_vkeys'].keys():
#         #         int_arckey = arcs[arckey]['int_vkeys'][vkey]
#         #         all_pt += arcs[int_arckey]['end_vkeys']
#         #     print 'all_pt', all_pt
#         #     if is_coplanar([egi.vertex_coordinates(vkey) for vkey in all_pt]):
#         #         new_arcs[arckey] = arcs[arckey]

#         #     else:
#         #         for vkey in arcs[arckey]['int_vkeys'].keys():
#         #             int_arckey = arcs[arckey]['int_vkeys'][vkey]
#         #             arcs[int_arckey]['vkeys'].remove(vkey)
#         #             del arcs[int_arckey]['int_vkeys'][vkey]
#         #             del egi.vertex[vkey]
#         # else:
#         #     new_arcs[arckey] = arcs[arckey]

#         new_arcs[arckey] = arcs[arckey]

#     # ==========================================================================
#     #   5.  Reorder vertices along each arc and add edges to EGI network
#     # ==========================================================================
#     for arckey in new_arcs:
#         vkeys = new_arcs[arckey]['vkeys']
#         if len(vkeys) > 2:
#             pt_list = [egi.vertex_coordinates(e_vkey) for e_vkey in vkeys]
#             new_arcs[arckey]['vkeys'] = _reorder_pts_on_arc(pt_list,
#                                                        new_arcs[arckey]['vkeys'],
#                                                        new_arcs[arckey]['arc'])[1]
#             edge_type = 'cross'
#         else:
#             edge_type = 'main'
#         for i in range(len(new_arcs[arckey]['vkeys']) - 1):
#             vkey_1 = new_arcs[arckey]['vkeys'][i]
#             vkey_2 = new_arcs[arckey]['vkeys'][i + 1]
#             egi.vertex[vkey_1]['nbrs'] += [vkey_2]
#             egi.vertex[vkey_2]['nbrs'] += [vkey_1]
#             egi.add_edge(vkey_1, vkey_2)
#             egi.edge[vkey_1][vkey_2] = {'type' : edge_type}

#     # # ==========================================================================
#     # #   5.  Reorder vertices along each arc and add edges to EGI network
#     # # ==========================================================================
#     # for arckey in arcs:
#     #     vkeys = arcs[arckey]['vkeys']
#     #     if len(vkeys) > 2:
#     #         pt_list = [egi.vertex_coordinates(vkey) for vkey in vkeys]
#     #         arcs[arckey]['vkeys'] = reorder_pts_on_arc(pt_list,
#     #                                                    arcs[arckey]['vkeys'],
#     #                                                    arcs[arckey]['arc'])[1]
#     #         edge_type = 'cross'
#     #     else:
#     #         edge_type = 'main'
#     #     for i in range(len(arcs[arckey]['vkeys']) - 1):
#     #         vkey_1 = arcs[arckey]['vkeys'][i]
#     #         vkey_2 = arcs[arckey]['vkeys'][i + 1]
#     #         egi.vertex[vkey_1]['nbrs'] += [vkey_2]
#     #         egi.vertex[vkey_2]['nbrs'] += [vkey_1]
#     #         egi.add_edge(vkey_1, vkey_2)
#     #         egi.edge[vkey_1][vkey_2] = {'type' : edge_type}
#     # ==========================================================================
#     #   6.  For each vertex, sort nbrs in ccw order
#     # ==========================================================================

#     _egi_sort_v_nbrs(egi)
#     # ==========================================================================
#     #   7.  Add EGI Network faces
#     # ==========================================================================

#     _egi_find_faces(egi)

#     # ==========================================================================
#     #   8.  Add ghost vertices and complete EGI
#     # ==========================================================================
#     # _egi_add_ghost_vertices(egi)

#     # timer --------------------------------------------------------------------
#     print ("--- egi network in %s seconds ---" % (time.time() - start_time))
#     return egi


# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# #   cells
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def create_unit_cell(egi_network):
#     cell = unit_polyhedron(egi_network)
#     draw_cell(cell,
#               layer='EGI::EGI_cell',
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=True,
#               show_face_labels=False,
#               show_vertex_labels=False,
#               vertex_color=None,
#               edge_color=None,
#               face_color=None)



#     return cell


# def unit_polyhedron(egi_network):

#     # timer --------------------------------------------------------------------
#     start_time = time.time()

#     # ==========================================================================
#     #   Initialize
#     # ==========================================================================
#     # origin      = egi_network.attributes['origin']
#     cell        = Mesh()
#     cell.name   = 'cell'
#     cell.face_type = {}
#     # ==========================================================================
#     #   Add vertices
#     # ==========================================================================
#     for fkey in egi_network.face:
#         x, y, z = egi_network.face_center(fkey)
#         cell.add_vertex(key=fkey, x=x, y=y, z=z)

#     # ==========================================================================
#     #   Add edges
#     # ==========================================================================
#     for vkey in egi_network.vertex:
#         cell_face = egi_network.vertex_faces(vkey, ordered=True)
#         cell.add_face(cell_face, fkey=vkey)
#         cell.face_type[vkey] = egi_network.vertex[vkey]['type']

#     for fkey in cell.faces():
#         for u, v in cell.face_halfedges(fkey):
#             if u in cell.edge and v in cell.edge[u]:
#                 continue
#             if v in cell.edge and u in cell.edge[v]:
#                 continue
#             cell.add_edge(u, v)


#     # timer --------------------------------------------------------------------
#     print ("--- unit polyhedron generated in %s seconds ---" % (time.time() - start_time))
#     return cell



# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# #   EGI Helpers
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def _egi_sort_v_nbrs(egi):
#     """ By default, the sorting should be ccw, since the circle is typically drawn
#     ccw around the local plane's z-axis...
#     """
#     xyz = {key: egi.vertex_coordinates(key) for key in egi.vertex}
#     # for key in egi.vertex:
#     #     attr

#     # xyz = dict((key, [attr[_] for _ in 'xyz']) for key, attr in egi.vertices_iter(True))

#     for vkey in egi.vertex:
#         nbrs    = egi.vertex[vkey]['nbrs']
#         plane   = Plane(Point3d(*xyz[vkey]),
#                         Vector3d(*[axis for axis in egi.vertex[vkey]['normal']]))
#         circle  = Circle(plane, 1)
#         p_list  = []
#         for nbr_vkey in nbrs:
#             boolean, parameter = ArcCurve(circle).ClosestPoint(Point3d(*xyz[nbr_vkey]))
#             p_list.append(parameter)
#         sorted_nbrs = [key for (param, key) in sorted(zip(p_list, nbrs))]
#         egi.vertex[vkey]['sorted_nbrs'] = sorted_nbrs


# def _egi_find_edge_face(u, v, egi):
#     """ same as duality.algorithms.find_edge_faces... using 'sorted_nbrs' instead
#     """
#     cycle = [u]
#     while True:
#         cycle.append(v)
#         nbrs    = egi.vertex[v]['sorted_nbrs']
#         nbr     = nbrs[nbrs.index(u) - 1]
#         u, v    = v, nbr
#         if v == cycle[0]:
#             cycle.append(v)
#             break
#     face = egi.add_face(cycle)
#     return face


# def _egi_find_faces(egi):
#     """ Modified, and simplified version of duality.algorithms.find_network_faces...
#     since there are no leaves or open faces in a egi network.
#     """
#     # del egi.face
#     egi.face = {}
#     egi.face_count = 0
#     del egi.halfedge
#     egi.halfedge = {key: {} for key in egi.vertices()}
#     for u, v in egi.edges():
#         egi.halfedge[u][v] = None
#         egi.halfedge[v][u] = None
#     u = sorted(egi.vertices(data=True), key=lambda x: (x[1]['y'], x[1]['x']))[0][0]
#     v = _find_first_neighbour(u, egi)

#     _egi_find_edge_face(u, v, egi)

#     for u, v in egi.edges():
#         if egi.halfedge[u][v] is None:
#             _egi_find_edge_face(u, v, egi)
#         if egi.halfedge[v][u] is None:
#             _egi_find_edge_face(v, u, egi)

#     return egi.face


# def _egi_add_ghost_vertices(egi):
#     """ Finds, and triangulates faces with more than 3 vertices. A quad face means
#     the corresponding dual vertex has four edges merging at it... therefore the
#     face-push/pull transformation during arearization algorithm will not work.

#     Also, the initial "unit" polyhedron should not have any vertices with more
#     than four edges, because this polyhedron show every possible connectivity of
#     the faces... By the cross-adjacency rule, four edges at a vertex means there
#     is a zero-area face there.
#     """
#     origin = egi.attributes['origin']
#     for fkey in egi.face:
#         face_vkeys = egi.face[fkey][:-1]
#         if len(face_vkeys) > 3:
#             face_center     = centroid_polyhedron([egi.vertex_coordinates(key) for key in face_vkeys])
#             new_vkey        = max(int(vkey) for vkey in egi.vertex.keys()) + 1
#             new_normal      = Vector(face_center, start=origin)
#             new_normal.normalize()
#             new_vertex_xyz  = [sum(axis) for axis in zip(new_normal, origin)]
#             egi.add_vertex(x=new_vertex_xyz[0],
#                            y=new_vertex_xyz[1],
#                            z=new_vertex_xyz[2],
#                            key=new_vkey,
#                            attr_dict={'type'        : 'ghost',
#                                       'normal'      : new_normal,
#                                       'magnitude'   : 0,
#                                       'nbrs'        : face_vkeys})
#             for vkey in face_vkeys:
#                 egi.vertex[vkey]['nbrs'] += [new_vkey]
#                 egi.add_edge(vkey, new_vkey)
#                 egi.edge[vkey][new_vkey] = {'type' : 'ghost'}
#     _egi_sort_v_nbrs(egi)
#     _egi_find_faces(egi)


# def _reorder_pts_on_arc(pt_list, pt_key_list, arc_curve):
#     # all points should be on the arc...
#     dist_list = []
#     sp = arc_curve.PointAtStart
#     for pt in pt_list:
#         dist_list.append(distance_point_point(sp, pt))
#     ordered_pt_list     = [x for (y, x) in sorted(zip(dist_list, pt_list))]
#     ordered_pt_key_list = [x for (y, x) in sorted(zip(dist_list, pt_key_list))]
#     return ordered_pt_list, ordered_pt_key_list


# def _curve_curve_intx(curve_1, curve_2):
#     intersection_tolerance  = 0.01
#     overlap_tolerance       = 0.0
#     intersection            = CCX(curve_1,
#                                   curve_2,
#                                   intersection_tolerance,
#                                   overlap_tolerance)
#     if not intersection:
#         return None
#     for instance in intersection:
#         return instance.PointA


# def draw_dot(labels):
#     guids = []
#     for l in iter(labels):
#         pos   = l['pos']
#         text  = l['text']
#         name  = l.get('name', '')
#         color = l.get('color', None)
#         layer = l.get('layer')
#         guid  = add_dot(text, Point3d(*pos))
#         if not guid:
#             continue
#         obj = find_object(guid)
#         if not obj:
#             continue
#         attr = obj.Attributes
#         if color:
#             attr.ObjectColor = FromArgb(*color)
#             attr.ColorSource = ColorFromObject
#         if layer:
#             index = find_layer_by_fullpath(layer, True)
#             if index >= 0:
#                 attr.LayerIndex = index
#         attr.Name = name
#         obj.CommitChanges()
#         guids.append(guid)
#     return guids


# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************
# #
# #   drawing
# #
# # ******************************************************************************
# # ******************************************************************************
# # ******************************************************************************


# def draw_egi(egi,
#              as_lines=False,
#              show_faces=False,
#              show_vertices=True,
#              show_labels=False,
#              show_edges=False,
#              delete=False):
#     # make EGI layers ----------------------------------------------------------
#     origin = egi.attributes['origin']
#     egi.layer = 'EGI'
#     # delete any existing ------------------------------------------------------
#     rhino.delete_objects(rhino.get_objects('{0}.vertex.*'.format(egi.name)))
#     rhino.delete_objects(rhino.get_objects('{0}.edge.*'.format(egi.name)))

#     if not delete:
#         #   vertices -----------------------------------------------------------
#         points  = []
#         vkeys   = []
#         for vkey in egi.vertex:
#             pos     = egi.vertex_coordinates(vkey)
#             name    = '{0}.vertex.{1}'.format(egi.name, vkey)
#             if 'type' in egi.vertex[vkey]:
#                 v_type  = egi.vertex[vkey]['type']
#                 if v_type   == 'face':
#                     v_color = (0, 0, 0)
#                     v_layer = 'EGI::EGI_vertices_face'
#                 elif v_type == 'zero':
#                     v_color = (207, 0, 0)
#                     v_layer = 'EGI::EGI_vertices_zero'
#                 elif v_type == 'ghost':
#                     v_color = (255, 191, 0)
#                     v_layer = 'EGI::EGI_vertices_ghost'
#             else:
#                 v_color = (0, 0, 0)
#                 v_layer = 'EGI'
#             points.append({'pos'   : pos,
#                            'name'  : name,
#                            'color' : v_color,
#                            'layer' : v_layer})
#             vkeys.append({'name' : str(vkey),
#                           'text' : str(vkey),
#                           'pos'  : pos,
#                           'color': v_color,
#                           'layer': v_layer})
#         if show_vertices:
#             rhino.xdraw_points(points, clear=False, redraw=False)
#         if show_labels:
#             draw_dot(vkeys)
#         #   edges --------------------------------------------------------------
#         if show_edges:
#             if as_lines:
#                 lines  = []
#                 for u, v in egi.edges_iter():
#                     e_type      = egi.edge[u][v]['type']
#                     if e_type   == 'main':
#                         e_color = (0, 0, 0)
#                     elif e_type == 'cross':
#                         e_color = (207, 0, 0)
#                     elif e_type == 'ghost':
#                         e_color = (255, 191, 0)
#                     start = egi.vertex_coordinates(u)
#                     end   = egi.vertex_coordinates(v)
#                     name  = '{0}.edge.{1}-{2}'.format(egi.name, u, v)
#                     lines.append({'start' : start,
#                                   'end'   : end,
#                                   'name'  : name,
#                                   'color' : e_color,
#                                   'arrow' : 'end',
#                                   'layer' : 'EGI::EGI_edges'})
#                 rhino.xdraw_lines(lines, redraw=True)
#             # as arcs --------------------------------------------------------------
#             else:
#                 for u, v in egi.edges():
#                     e_type      = egi.edge[u][v]['type']
#                     if e_type   == 'main':
#                         e_color = (0, 0, 0)
#                     elif e_type == 'cross':
#                         e_color = (207, 0, 0)
#                     elif e_type == 'ghost':
#                         e_color = (207, 0, 0)
#                     normal_1    = egi.vertex[u]['normal']
#                     normal_2    = egi.vertex[v]['normal']
#                     arc         = _draw_arc(normal_1, normal_2, origin)
#                     guid        = add_curve(arc)
#                     obj         = find_object(guid)
#                     attr                    = obj.Attributes
#                     attr.ObjectColor        = FromArgb(*e_color)
#                     attr.ColorSource        = ColorFromObject
#                     attr.ObjectDecoration   = EndArrowhead
#                     index = find_layer_by_fullpath('EGI::EGI_arcs', True)
#                     if index >= 0:
#                         attr.LayerIndex = index
#                     obj.CommitChanges()



# def draw_cell(cell,
#               layer,
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=False,
#               show_face_labels=True,
#               show_vertex_labels=True,
#               vertex_color=None,
#               edge_color=None,
#               face_color=None,
#               delete=False):

#     rs.EnableRedraw(False)
#     # set default options ------------------------------------------------------
#     if not isinstance(vertex_color, dict):
#         vertex_color = {}
#     if not isinstance(edge_color, dict):
#         edge_color = {}
#     if not isinstance(face_color, dict):
#         face_color = {}
#     # delete all relevant objects by name --------------------------------------
#     name = cell.name
#     objects  = rhino.get_objects(name=cell.name)
#     objects += rhino.get_objects(name='*.poly.*')
#     objects += rhino.get_objects(name='{0}.face.*'.format(cell.name))
#     objects += rhino.get_objects(name='{0}.vertex.*'.format(cell.name))
#     objects += rhino.get_objects(name='{0}.edge.*'.format(cell.name))
#     rhino.delete_objects(objects)
#     # clear the relevant layers ------------------------------------------------
#     if clear:
#         rhino.clear_layers((layer))

#     if not delete:
#         # ==========================================================================
#         #   faces
#         # ==========================================================================
#         if show_faces:
#             faces = []
#             for fkey in cell.face:
#                 face_type = cell.face_type[fkey]
#                 if face_type    == 'face':
#                     color = (0, 0, 0)
#                     layer = 'EGI::EGI_cell'
#                 elif face_type == 'zero':
#                     color = (0, 255, 0)
#                     layer = 'EGI::EGI_cell_zero'
#                 elif face_type == 'ghost':
#                     color = (255, 191, 0)
#                 else:
#                     color = cell.attributes['color.face']


#                 f_vkeys = cell.face[fkey]
#                 f_v_xyz = [cell.vertex_coordinates(vkey) for vkey in f_vkeys]
#                 f_v_xyz.append(f_v_xyz[0])
#                 faces.append({'points' : f_v_xyz,
#                               'name'   : '{0}.face.{1}.{2}'.format(name, fkey, cell.face[fkey]),
#                               'layer'  : layer,
#                               'color'  : color})
#             rhino.xdraw_faces(faces,
#                               redraw=(True if redraw and not (show_vertices or show_edges) else False))

#         if show_face_labels:
#             f_labels = []
#             for fkey in cell.face:
#                 f_labels.append({'name' : '{0}.face.{1}'.format(cell.name, fkey),
#                                  'text' : str(fkey),
#                                  'pos'  : cell.face_center(fkey),
#                                  'color': (255, 0, 0),
#                                  'layer': 'cell'})
#             rhino.xdraw_labels(f_labels)
#         # ==========================================================================
#         #   edges
#         # ==========================================================================
#         if show_edges:
#             lines = []
#             if edge_color is not None:
#                 color = edge_color
#             else:
#                 color = cell.attributes['color.edge']
#             for u, v in cell.edges():
#                 lines.append({'start': cell.vertex_coordinates(u),
#                               'end'  : cell.vertex_coordinates(v),
#                               'name' : '{0}.edge.{1}-{2}'.format(name, u, v),
#                               'color': color})
#             rhino.xdraw_lines(lines,
#                               layer='EGI::EGI_edges',
#                               clear=False,
#                               redraw=False)
#         # ==========================================================================
#         #   vertices
#         # ==========================================================================
#         if show_vertices:
#             points = []
#             color  = cell.attributes['color.vertex']
#             for key in cell.vertex:
#                 points.append({'pos'  : cell.vertex_coordinates(key),
#                                'name' : '{0}.vertex.{1}'.format(name, key),
#                                'color': vertex_color.get(key, color)})
#             rhino.xdraw_points(points,
#                                layer=layer,
#                                clear=False,
#                                redraw=False)
#         # ==========================================================================
#         #   vertex labels
#         # ==========================================================================
#         if show_vertex_labels:
#             vkeys   = []
#             for vkey in cell.vertex:
#                 pos   = cell.vertex_coordinates(vkey)
#                 color = (255, 255, 255)
#                 layer = 'cell'
#                 vkeys.append({'name' : '{0}.vertex.{1}'.format(cell.name, vkey),
#                               'text' : str(vkey),
#                               'pos'  : cell.vertex_coordinates(vkey),
#                               'color': color,
#                               'layer': layer})
#             rhino.xdraw_labels(vkeys)

#         # redraw the views if so requested -----------------------------------------
#         if redraw:
#             rs.Redraw()






# def arearize(cell,
#              egi,
#              count=100,
#              step=0.01,
#              factor=0.1,
#              threshold=0.001,
#              draw_rs_lines=False,
#              adaptive=False,
#              conduit=True,
#              export=False,
#              file_name='file_name'):

#     rs.EnableRedraw(True)

#     # ==========================================================================
#     #   start loop
#     # ==========================================================================
#     iteration_count = 0
#     start_time = time.time()
#     face_vkeys_dict = dict((fkey, cell.face[fkey]) for fkey in cell.face)

#     while count:
#         new_xyz         = dict((vkey, []) for vkey in cell.vertex)
#         current_areas   = dict((fkey, cell.face_area(fkey)) for fkey in cell.face)
#         area_difference = dict((fkey, _area_deficit(cell, egi, fkey)) for fkey in cell.face)

#         print "iteration_count -------------------------------", iteration_count
#         for fkey in cell.face:
#             f_center  = cell.face_center(fkey)
#             f_vkeys   = face_vkeys_dict[fkey]
#             delta     = area_difference[fkey]
#             f_plane   = (f_center, egi.vertex[fkey]['normal'])
#             target_area = egi.vertex[fkey]['magnitude']


#             # ------------------------------------------------------------------
#             # NON-ZERO FACES
#             # ------------------------------------------------------------------
#             if target_area != 0:
#                 if is_face_selfintersecting (cell, fkey):
#                     new_face = _scale_polygon_by_factor(cell, fkey, 1 + (delta / abs(delta)) * factor)
#                 else:
#                     new_face  = _scale_polygon_by_area(cell, egi, fkey, target_area, draw=draw_rs_lines)
#                 for vkey in new_face:
#                     new_xyz[vkey].append(new_face[vkey])

#             # ------------------------------------------------------------------
#             # ZERO FACES
#             # ------------------------------------------------------------------
#             elif target_area == 0:

#                 if is_face_selfintersecting (cell, fkey):
#                     new_face = _scale_polygon_by_factor(cell, fkey, 1 - factor)
#                 else:
#                     polygon   = [cell.vertex_coordinates(vkey) for vkey in f_vkeys]  # f vertex coordinates
#                     projected = [project_point_plane(pt, f_plane) for pt in polygon]
#                     projected.append(projected[0])
#                     offset = offset_polygon(projected, delta * step * -1)
#                     new_face = {}
#                     for i in range(len(f_vkeys)):
#                         new_face[f_vkeys[i]] = offset[i]

#                 for vkey in new_face:
#                     new_xyz[vkey].append(new_face[vkey])


#         # collapse short edges -------------------------------------------------
#         for u, v in cell.edges():
#             dist = cell.edge_length(u, v)
#             if dist < 0.1:
#                 mid_pt = midpoint_line((cell.vertex_coordinates(u), cell.vertex_coordinates(v)))
#                 new_xyz[u].append(mid_pt)
#                 new_xyz[v].append(mid_pt)

#         # compute final v xyz --------------------------------------------------
#         for vkey in new_xyz:
#             final_xyz = [sum(axis) for axis in zip(*new_xyz[vkey])]
#             final_xyz = [xyz / len(new_xyz[vkey]) for xyz in final_xyz]
#             cell.vertex[vkey]['x'] = final_xyz[0]
#             cell.vertex[vkey]['y'] = final_xyz[1]
#             cell.vertex[vkey]['z'] = final_xyz[2]



#         # check threshold ------------------------------------------------------
#         max_diff = max([abs(area_difference[fkey]) for fkey in cell.face])
#         if max_diff < threshold:
#             break
#         elif max(current_areas.values()) > 30:
#             print "SOMETHING WENT WRONG !"
#             break
#         sc.doc.Views.Redraw()
#         count           -= 1
#         iteration_count += 1



#     # ==========================================================================
#     #   end loop and update
#     # ==========================================================================
#     print '------------------ arearization finished in:'
#     print (time.time() - start_time), 'seconds'
#     print iteration_count, 'iterations'


#     draw_cell(cell,
#               layer='EGI_cell',
#               clear=False,
#               redraw=True,
#               show_faces=True,
#               show_vertices=False,
#               show_edges=True,
#               show_face_labels=False,
#               show_vertex_labels=False,
#               vertex_color=None,
#               edge_color=(255, 0, 0),
#               face_color=None)

#     return cell


# def _scale_polygon_by_area(cell, egi, fkey, target_area, adaptive=False, draw=False):
#     """ scales a cell face by
#     """
#     # evaluate current face ----------------------------------------------------
#     center       = cell.face_center(fkey)
#     f_vkeys      = cell.face[fkey]
#     polygon      = [cell.vertex_coordinates(vkey) for vkey in f_vkeys]
#     current_area = cell.face_area(fkey)
#     factor       = (target_area / current_area)**0.5

#     # get target plane ---------------------------------------------------------
#     if adaptive:
#         target_plane = bestfit_plane_from_points(polygon)
#     else:
#         target_plane = (center, egi.vertex[fkey]['normal'])
#     projected = [project_point_plane(pt, target_plane) for pt in polygon]

#     # scale face + compute new vertex xyz --------------------------------------
#     new_face_v_xyz = {}
#     for i in range(len(f_vkeys)):
#         vertex = projected[i]
#         vector = normalize_vector(subtract_vectors(vertex, center))
#         dist = distance_point_point(center, vertex)
#         xyz = add_vectors(center, scale_vector(vector, factor * dist))
#         new_face_v_xyz[f_vkeys[i]] = xyz

#     return new_face_v_xyz


# def _scale_polygon_by_factor(cell, fkey, factor):
#     center       = cell.face_center(fkey)
#     f_vkeys      = cell.face_vertices(fkey, ordered=True)

#     new_face_v_xyz = {}
#     for vkey in f_vkeys:
#         vertex = cell.vertex_coordinates(vkey)
#         vector = normalize_vector(subtract_vectors(vertex, center))
#         dist = distance_point_point(center, vertex)
#         xyz = add_vectors(center, scale_vector(vector, factor * dist))
#         new_face_v_xyz[vkey] = xyz

#     return new_face_v_xyz


# def _area_deficit(cell, egi, fkey):
#     current_area = cell.face_area(fkey)
#     target_area  = egi.vertex[fkey]['magnitude']
#     difference   = target_area - current_area
#     return difference


# def is_face_selfintersecting (cell, fkey):
#     # get list of face vkeys (first and last not the same)
#     face_vkeys = cell.face[fkey]

#     v_geokeys = dict((geometric_key(cell.vertex_coordinates(vkey)), vkey) for vkey in face_vkeys)

#     edges = []
#     for i in range(-1, len(face_vkeys)-1):
#         edges.append((face_vkeys[i], face_vkeys[i + 1]))
#     for u1, v1 in edges:
#         for u2, v2 in edges:
#             if u1 == u2 or v1 == v2 or u1 == v2 or u2 == v1:
#                 continue
#             else:
#                 a = cell.vertex_coordinates(u1)
#                 b = cell.vertex_coordinates(v1)
#                 c = cell.vertex_coordinates(u2)
#                 d = cell.vertex_coordinates(v2)

#                 int_1, int_2 = intersection_line_line((a, b), (c, d))
#                 if int_1 is not None or int_2 is not None:
#                     if is_point_on_segment(int_1, (a, b)) or is_point_on_segment(int_2, (c, d)):
#                         if str(geometric_key(int_1)) not in v_geokeys or str(geometric_key(int_2)) not in v_geokeys:
#                             return True

#     return False