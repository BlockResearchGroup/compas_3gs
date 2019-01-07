from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import project_point_plane

from compas.geometry.algorithms.bestfit import bestfit_plane

from compas_rhino.conduits.edges import LinesConduit







def volmesh_planarize_faces(volmesh,
                            count=500,
                            tolerance=0.001):

    edges = []
    for u, v in volmesh.edges():
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        edges.append((u_xyz, v_xyz))

    conduit = LinesConduit(edges)
    conduit.Enabled = True

    iteration = 0

    while count:

        deviation = 0

        new_vertices = {vkey: [] for vkey in volmesh.vertex}

        for hfkey in volmesh.faces():
            hf_vkeys = volmesh.halfface_vertices(hfkey)
            points = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            plane = bestfit_plane(points)
            for vkey in hf_vkeys:
                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                dist = distance_point_point(xyz, new_xyz)
                if dist > deviation:
                    deviation = dist
                new_vertices[vkey].append(new_xyz)

        for vkey in new_vertices:
            final_xyz = centroid_points(new_vertices[vkey])
            volmesh.vertex_update_xyz(vkey, final_xyz)

        if deviation < tolerance:
            break

        edges = []
        for u, v in volmesh.edges():
            u_xyz = volmesh.vertex_coordinates(u)
            v_xyz = volmesh.vertex_coordinates(v)
            edges.append((u_xyz, v_xyz))

        conduit.lines = edges

        conduit.redraw()
        count     -= 1
        iteration += 1

    conduit.Enabled = False
    del conduit

    print('planarization ended at:', iteration)
    print('deviation:', deviation)

    volmesh.draw(layer='forcepolyhedra')


