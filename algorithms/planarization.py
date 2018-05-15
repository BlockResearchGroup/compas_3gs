import rhinoscriptsyntax as rs

from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import project_point_plane

from compas.geometry.algorithms.bestfit import bestfit_plane

from compas_rhino.utilities import xdraw_lines
from compas_rhino.utilities import xdraw_labels
from compas_rhino.utilities import xdraw_polylines
from compas_rhino.utilities import xdraw_points

from compas_rhino.conduits.edges import LinesConduit


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


def volmesh_planarize_faces(volmesh,
                            count=1,
                            target_normals=None,
                            tolerance=0.001):

    edges = []
    for u, v in volmesh.edges():
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        edges.append((u_xyz, v_xyz))

    # conduit = LinesConduit(edges)
    # conduit.Enabled = True

    iteration = 0

    hfkeys = volmesh.faces()
    if target_normals:
        hfkeys = target_normals.keys()

    init_hf_centers = {}
    for hfkey in volmesh.halffaces_on_boundary():
        init_hf_centers[hfkey] = volmesh.halfface_center(hfkey)

    print(hfkeys)

    while count:

        deviation = 0

        new_vertices = {}

        polylines = []

        for hfkey in hfkeys:

            hf_center = volmesh.halfface_center(hfkey)
            if hfkey in init_hf_centers:
                hf_center = init_hf_centers[hfkey]

            hf_vkeys = volmesh.halfface_vertices(hfkey)
            points = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]

            if not target_normals:
                plane = bestfit_plane(points)

            else:
                plane = (hf_center, target_normals[hfkey])

            projected_pts = []
            for vkey in hf_vkeys:
                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                dist = distance_point_point(xyz, new_xyz)
                if dist > deviation:
                    deviation = dist
                if vkey not in new_vertices:
                    new_vertices[vkey] = []
                new_vertices[vkey].append(new_xyz)
                projected_pts.append(new_xyz)

        #     name = 'surface-iteration.{}'.format(iteration)
        #     rs.AddLayer(name)
        #     rs.CurrentLayer(name)
        #     rs.AddSrfPt(projected_pts)

        #     polylines.append(
        #         {'points' : projected_pts + [projected_pts[0]],
        #          'name'   : 'iteration.{}-hfkey.{}'.format(iteration, hfkey)})

        # points = []

        # arrows = []

        # print(new_vertices)

        for vkey in new_vertices:
            if vkey:
                final_xyz = centroid_points(new_vertices[vkey])
                volmesh.vertex_update_xyz(vkey, final_xyz)

                # for each_pt in new_vertices[vkey]:
                #     arrows.append(
                #         {'start' : each_pt,
                #          'end'   : final_xyz,
                #          'color' : (0, 255, 0),
                #          'arrow' : 'end',
                #          'name'  : 'iteration.{}-vkey.{}'.format(iteration, vkey)})

                # points.append(
                #     {'pos' : final_xyz,
                #      'color': (0, 0, 255),
                #      'name': 'iteration.{}-vkey.{}'.format(iteration, vkey)})


        # ----------------------------------------------------------------------

        if deviation < tolerance:
            break

        # edges = []
        # for u, v in volmesh.edges():
        #     u_xyz = volmesh.vertex_coordinates(u)
        #     v_xyz = volmesh.vertex_coordinates(v)
        #     edges.append((u_xyz, v_xyz))

        # # conduit.lines = edges

        # # conduit.redraw()
        # count     -= 1
        # iteration += 1

        # name = 'others-iteration.{}'.format(iteration)
        # rs.AddLayer(name)
        # rs.CurrentLayer(name)

        # xdraw_lines(arrows)

        # xdraw_points(points)

        # name = 'polylines-iteration.{}'.format(iteration)
        # rs.AddLayer(name)
        # rs.CurrentLayer(name)

        # xdraw_polylines(polylines)

    # conduit.Enabled = False
    # del conduit

    print('planarization ended at:', iteration)
    print('deviation:', deviation)

    # volmesh.clear()
    # volmesh.draw(layer='forcepolyhedra')


def _store_initial_normals(volmesh):

    for hfkey in volmesh.halfface:
        center = volmesh.halfface_center(hfkey)
        normal = volmesh.halfface_normal(hfkey)
        volmesh.update_f_data(
            hfkey,
            attr_dict={'normal_i': normal, 'center_i': center})

    return volmesh
