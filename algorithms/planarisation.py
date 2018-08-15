import rhinoscriptsyntax as rs
import scriptcontext as sc

from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import project_point_plane

from compas.geometry.algorithms.bestfit import bestfit_plane

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_polylines
from compas_rhino.utilities import xdraw_points

from compas_3gs.rhino import planarisation_conduit

from compas_rhino.helpers.volmesh import volmesh_select_vertices


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


def volmesh_planarise_faces(volmesh,
                            count=100,
                            target_normals=None,
                            target_centers=None,
                            conduit=True,
                            tolerance=0.00001):


    omit_vkeys = volmesh_select_vertices(volmesh)

    # conduit ------------------------------------------------------------------
    if conduit:
        conduit = planarisation_conduit(volmesh)
        conduit.Enabled = True


    iteration = 0


    edges = []
    polylines = []



    while count:

        deviation = 0

        new_vertices = {}


        for hfkey in volmesh.halfface:

            hf_vkeys  = volmesh.halfface_vertices(hfkey)
            points    = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            hf_normal = bestfit_plane(points)[1]
            hf_center = volmesh.halfface_center(hfkey)

            if target_normals:
                if hfkey in target_normals:
                    hf_normal = target_normals[hfkey]

            if target_centers:
                if hfkey in target_centers:
                    hf_center = target_centers[hfkey]

            plane = (hf_center, hf_normal)


            projected_pts = []
            for vkey in hf_vkeys:

                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                dist    = distance_point_point(xyz, new_xyz)

                # if vkey == 0:
                    # print(hfkey, dist)
                    # rs.AddPoint(new_xyz)

                if dist > deviation:
                    deviation = dist
                if vkey not in new_vertices:
                    new_vertices[vkey] = []
                new_vertices[vkey].append(new_xyz)
                projected_pts.append(new_xyz)

            # name = 'surface-iteration.{}'.format(iteration)
            # rs.AddLayer(name)
            # rs.CurrentLayer(name)

            # if 0 in hf_vkeys:
            #     polylines.append(
            #         {'points' : projected_pts + [projected_pts[0]],
            #          'layer'  : name,
            #          'name'   : 'iteration.{}-hfkey.{}'.format(iteration, hfkey)})


        for vkey in new_vertices:
            if vkey not in omit_vkeys:
                final_xyz = centroid_points(new_vertices[vkey])
                volmesh.vertex_update_xyz(vkey, final_xyz)

        # ----------------------------------------------------------------------


        if iteration > 1 and deviation < tolerance:
            break


        sc.doc.Views.Redraw()
        iteration += 1
        count -= 1


        # if (iteration % 5) == 0:

        #     name = 'iteration.{}'.format(iteration)
        #     rs.AddLayer(name)
        #     rs.CurrentLayer(name)

        #     # name = 'polylines-iteration.{}'.format(iteration)
        #     # rs.AddLayer(name)
        #     # rs.CurrentLayer(name)



        #     for u, v in volmesh.edges():
        #         u_xyz = volmesh.vertex_coordinates(u)
        #         v_xyz = volmesh.vertex_coordinates(v)


        #         edges.append(
        #             {'start' : u_xyz,
        #              'end'   : v_xyz,
        #              'color' : (0, 255, 0),
        #              'layer' : name,
        #              'name'  : 'iteration-{}.{}-{}'.format(iteration, u, v)})



    if conduit:
        conduit.Enabled = False
        del conduit

    # xdraw_lines(edges)
    # xdraw_polylines(polylines)

    print('planarisation ended at:', iteration)
    print('deviation:', deviation)

    volmesh.clear()
    volmesh.draw(layer='forcepolyhedra')




def _store_initial_normals(volmesh):

    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        volmesh.update_f_data(
            hfkey,
            attr_dict={'normal_i': normal, 'center_i': center})

    return volmesh










# def volmesh_planarise_faces(volmesh,
#                             count=100,
#                             target_normals=None,
#                             conduit=True,
#                             tolerance=0.00001):

#     edges = []
#     for u, v in volmesh.edges():
#         u_xyz = volmesh.vertex_coordinates(u)
#         v_xyz = volmesh.vertex_coordinates(v)
#         edges.append((u_xyz, v_xyz))

#     if conduit:
#         conduit = planarisation_conduit(volmesh)
#         conduit.Enabled = True

#     iteration = 0

#     hfkeys = volmesh.faces()
#     if target_normals:
#         hfkeys = target_normals.keys()

#     init_hf_centers = {}
#     for hfkey in volmesh.halffaces_on_boundary():
#         init_hf_centers[hfkey] = volmesh.halfface_center(hfkey)

#     # print(hfkeys)
#     rs.EnableRedraw(False)


#     polylines = []

#     points = []

#     arrows = []


#     while count:

#         deviation = 0

#         new_vertices = {}



#         for hfkey in hfkeys:

#             hf_center = volmesh.halfface_center(hfkey)
#             if hfkey in init_hf_centers:
#                 hf_center = init_hf_centers[hfkey]

#             hf_vkeys = volmesh.halfface_vertices(hfkey)
#             points = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]

#             if not target_normals:
#                 plane = bestfit_plane(points)

#             else:
#                 plane = (hf_center, target_normals[hfkey])

#             projected_pts = []
#             for vkey in hf_vkeys:
#                 xyz     = volmesh.vertex_coordinates(vkey)
#                 new_xyz = project_point_plane(xyz, plane)
#                 dist = distance_point_point(xyz, new_xyz)
#                 if dist > deviation:
#                     deviation = dist
#                 if vkey not in new_vertices:
#                     new_vertices[vkey] = []
#                 new_vertices[vkey].append(new_xyz)
#                 projected_pts.append(new_xyz)

#             name = 'surface-iteration.{}'.format(iteration)
#             rs.AddLayer(name)
#             rs.CurrentLayer(name)
#             # rs.AddSrfPt(projected_pts)

#             polylines.append(
#                 {'points' : projected_pts + [projected_pts[0]],
#                  'name'   : 'iteration.{}-hfkey.{}'.format(iteration, hfkey)})



#         print(new_vertices)

#         for vkey in new_vertices:
#             if vkey:
#                 final_xyz = centroid_points(new_vertices[vkey])
#                 volmesh.vertex_update_xyz(vkey, final_xyz)

#                 for each_pt in new_vertices[vkey]:
#                     arrows.append(
#                         {'start' : each_pt,
#                          'end'   : final_xyz,
#                          'color' : (0, 255, 0),
#                          'arrow' : 'end',
#                          'name'  : 'iteration.{}-vkey.{}'.format(iteration, vkey)})

#                 points.append(
#                     {'pos' : final_xyz,
#                      'color': (0, 0, 255),
#                      'name': 'iteration.{}-vkey.{}'.format(iteration, vkey)})


#         # ----------------------------------------------------------------------

#         if deviation < tolerance:
#             break

#         edges = []
#         for u, v in volmesh.edges():
#             u_xyz = volmesh.vertex_coordinates(u)
#             v_xyz = volmesh.vertex_coordinates(v)
#             edges.append((u_xyz, v_xyz))

#         # conduit.lines = edges

#         # conduit.redraw()
#         count     -= 1
#         iteration += 1


#     if conduit:
#         conduit.Enabled = False
#         del conduit



#     name = 'others-iteration.{}'.format(iteration)
#     rs.AddLayer(name)
#     rs.CurrentLayer(name)

#     xdraw_lines(arrows)

#     # xdraw_points(points)

#     name = 'polylines-iteration.{}'.format(iteration)
#     rs.AddLayer(name)
#     rs.CurrentLayer(name)

#     xdraw_polylines(polylines)


#     print('planarization ended at:', iteration)
#     print('deviation:', deviation)

#     volmesh.clear()
#     volmesh.draw(layer='forcepolyhedra')


# def _store_initial_normals(volmesh):

#     for hfkey in volmesh.halfface:
#         center = volmesh.halfface_center(hfkey)
#         normal = volmesh.halfface_normal(hfkey)
#         volmesh.update_f_data(
#             hfkey,
#             attr_dict={'normal_i': normal, 'center_i': center})

#     return volmesh
