from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.geometry import add_vectors
from compas.geometry import centroid_points
from compas.geometry import midpoint_point_point
from compas.geometry import subtract_vectors

from compas_rhino.utilities import draw_labels
from compas_rhino.utilities import draw_lines

from compas_3gs.algorithms import egi_from_vectors
from compas_3gs.algorithms import cell_planarise
from compas_3gs.algorithms import cell_from_egi

from compas_3gs.rhino import draw_egi_arcs
from compas_3gs.rhino import MeshConduit

from compas_3gs.utilities import get_index_colordict

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
#   1. get force vectors
# ------------------------------------------------------------------------------
lines  = rs.GetObjects("Select force vectors in equilibrium", preselect=True, filter=rs.filter.curve)
origin = rs.GetPoint("Pick origin")

midpts       = {}
vectors      = {}
target_areas = {}
for index, line in enumerate(lines):
    sp  = rs.CurveStartPoint(line)
    ep  = rs.CurveEndPoint(line)
    mp  = midpoint_point_point(sp, ep)
    mag = rs.CurveLength(line)
    midpts[index]       = mp
    vectors[index]      = subtract_vectors(ep, sp)
    target_areas[index] = mag


# ------------------------------------------------------------------------------
#   2. egi
# ------------------------------------------------------------------------------
egi = egi_from_vectors(vectors, origin)

egi_vertex_colordict = {}
for vkey in egi.vertex:
    color = (0, 0, 0)
    if egi.vertex[vkey]['type'] == 'zero':
        color = (255, 0, 0)
    egi_vertex_colordict[vkey] = color

# draw egi vertex labels and edgees as arcs
rs.AddLayer('egi')

egi.draw_vertexlabels(color=egi_vertex_colordict)
draw_egi_arcs(egi)

# pause
rs.EnableRedraw(True)
rs.GetString('EGI created ... Press Enter to generate unit cell ... ')


# ------------------------------------------------------------------------------
#   3. unit polyhedron
# ------------------------------------------------------------------------------
rs.AddLayer('cell')
cell = cell_from_egi(egi)
cell.draw_faces(color=egi_vertex_colordict)

# pause
rs.EnableRedraw(True)
rs.GetString('Zero faces are shown in red ... Press Enter to arearise cell faces ...')


# ------------------------------------------------------------------------------
#   4. arearise cell faces
# ------------------------------------------------------------------------------

# conduit
conduit = MeshConduit(cell)


def callback(cell, k, args):
    if k % 10:
        conduit.redraw()


# set targets for zero faces
for fkey in cell.faces():
    if fkey not in target_areas:
        target_areas[fkey] = 0

# set target normals
target_normals = {}
for fkey in cell.faces():
    target_normals[fkey] = egi.vertex[fkey]['normal']

collapse_edge_length = rs.GetReal("Collapse edge length?", number=0.1)

egi.clear()
cell.clear()

with conduit.enabled():
    cell_planarise(cell,
                   kmax=2000,
                   target_areas=target_areas,
                   target_normals=target_normals,
                   collapse_edge_length=collapse_edge_length,
                   callback=callback,
                   print_result_info=True)


# ------------------------------------------------------------------------------
#   5. draw results
# ------------------------------------------------------------------------------
rs.HideObjects(lines)

# get index colors
colordict = get_index_colordict(vectors.keys())

# draw initial vectors and target areas
input_vector_labels = []
input_vectors       = []
for i in vectors:
    label = 'target : ' + str(round(target_areas[i], 5))
    input_vector_labels.append({'pos'  : midpts[i],
                                'text' : label,
                                'color': colordict[i]})
    input_vectors.append({'start': list(origin),
                          'end'  : add_vectors(origin, vectors[i]),
                          'color': colordict[i],
                          'arrow': 'end'})
draw_labels(input_vector_labels)
draw_lines(input_vectors)

# diaplay final cell face areas
final_face_labels = []
for fkey in vectors:
    label = str(round(cell.face_area(fkey), 5))
    pos = centroid_points(cell.face_coordinates(fkey))
    final_face_labels.append({'pos': pos,
                              'text': label,
                              'color': colordict[fkey]})
draw_labels(final_face_labels)

# draw cell geometry
for fkey in target_areas:
    if target_areas[fkey] != 0:
        cell.draw_faces(keys=[fkey])
