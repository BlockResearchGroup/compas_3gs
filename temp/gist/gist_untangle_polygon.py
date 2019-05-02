from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs

from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import area_polygon
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import length_vector
from compas.geometry import normal_polygon
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import centroid_points
from compas.geometry import distance_point_point as distance
from compas.geometry import is_point_on_segment
from compas.geometry import intersection_line_line
from compas.geometry import midpoint_point_point

from compas.utilities import geometric_key

from compas_rhino.utilities import draw_labels
from compas_rhino.utilities import draw_lines
from compas_rhino.utilities import draw_faces


def untangle_polygon(points):

    def _cross_edges(edge1, edge2):
        a, b      = edge1
        c, d      = edge2
        edge1_vec = normalize_vector(subtract_vectors(b, a))
        edge2_vec = normalize_vector(subtract_vectors(d, c))
        cross     = cross_vectors(edge1_vec, edge2_vec)
        return cross

    xyz        = {i: points[i] for i in range(len(points))}
    vkeys      = range(len(points))

    count = 20
    while count:
        count -= 1
        moved = []
        for i in range(-1, len(points) - 1):
            t       = xyz[vkeys[i - 2]]
            u       = xyz[vkeys[i - 1]]
            v       = xyz[vkeys[i]]
            w       = xyz[vkeys[i + 1]]
            u_cross = _cross_edges((t, u), (u, v))
            v_cross = _cross_edges((u, v), (v, w))
            dot = dot_vectors(u_cross, v_cross)
            if dot < 0:
                midpt = midpoint_point_point(u, w)
                vec = scale_vector(subtract_vectors(midpt, v), 1.5)


                xyz[vkeys[i]] = add_vectors(v, vec)
                moved.append([vkeys[i]])
        if len(moved) == 0 :
            break

    lines = []
    for i in range(-1, len(points) - 1):
        u = xyz[vkeys[i]]
        v = xyz[vkeys[i + 1]]
        lines.append({
            'start': u,
            'end'  : v,
            'arrow': 'end',
            'color': (0, 0, 0),
            'name' : '{}-{}'.format(u, v)})
    draw_lines(lines)









# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    guid = rs.GetObject("select polysurfaces", filter=4)

    rs.HideObjects(guid)

    if not rs.IsCurveClosed(guid):
        print('not a closed polyline')

    points = [[pt.X, pt.Y, pt.Z] for pt in rs.PolylineVertices(guid)]
    points = points[:-1]

    result = untangle_polygon(points)
