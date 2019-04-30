from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino as rhino

from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector
from compas.geometry import distance_point_point
from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import centroid_points
from compas.geometry import midpoint_point_point
from compas.geometry import bestfit_plane
from compas.geometry import is_polygon_convex
from compas.geometry import project_points_plane

from compas.geometry.transformations.transformations import project_point_plane

from compas_rhino.helpers import volmesh_select_vertices

from compas.utilities import i_to_blue

# from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.operations import cell_collapse_short_edges

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented

from compas_3gs.utilities import scale_polygon



# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh arearisation
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

# volmesh_arearise = volmesh_planarise


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   arearisation helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _area_polygon_footprint(points):

    area = 0
    p    = len(points)
    w    = centroid_points(points)

    for i in range(-1, len(points) - 1):
        u      = points[i]
        v      = points[i + 1]
        uv     = subtract_vectors(v, u)
        vw     = subtract_vectors(w, v)
        normal = scale_vector(cross_vectors(uv, vw), 0.5)
        area   += length_vector(normal)

    return area





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
