from compas.geometry import distance_point_point
from compas.geometry import centroid_points
from compas.geometry import project_point_plane

from compas.geometry.algorithms.bestfit import bestfit_plane

__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


def planarize_VM(volmesh,
                 count=500,
                 tolerance=0.001):

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

        count     -= 1
        iteration += 1

    print('planarization ended at:', iteration)
    print('deviation:', deviation)

    volmesh.draw()
