from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules('compas')


from compas.geometry import add_vectors, centroid_points, midpoint_point_point, subtract_vectors

from compas_rhino.geometry import RhinoSurface
from compas_rhino.utilities import draw_labels, draw_lines

from compas_3gs.algorithms import egi_from_vectors, cell_planarise, cell_from_egi
from compas_3gs.rhino import draw_egi_arcs, MeshConduit
from compas_3gs.utilities import get_index_colordict
from compas_3gs.datastructures import Mesh3gsArtist

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

# select external force vectors in equilibrium
lines  = rs.GetObjects("Select force vectors in equilibrium", preselect=True, filter=rs.filter.curve)
# select the origin / node of the structure
origin = rs.GetPoint("Pick origin")

# save force data in dictionaries
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
# construct EGI from a set of equilibrated forces
egi = egi_from_vectors(vectors, origin) 

# draw vertex labels
egi_vertex_colordict = {}
for vkey in egi.vertex:
    # the intersection point of adjacent arcs is in red color
    if egi.vertex[vkey]['type'] == 'zero':
        color = (255, 0, 0)
    # the point mass of EGI is in black color
    else:
        color = (0, 0, 0)
    egi_vertex_colordict[vkey] = color

egiartist = Mesh3gsArtist(egi, layer='egi')
egiartist.draw_vertexlabels(color=egi_vertex_colordict)

# draw edgees as arcs
egi_arcs = draw_egi_arcs(egi)

# pause
rs.EnableRedraw(True)
rs.GetString('EGI created ... Press Enter to generate unit cell ... ')


# ------------------------------------------------------------------------------
#   3. unit polyhedron
# ------------------------------------------------------------------------------
# generate polyhedral cell from EGI, the face colors are the same as corresponding vertex colors
cell = cell_from_egi(egi)
cellartist = Mesh3gsArtist(cell, layer='cell')
cellartist.draw_faces(color=egi_vertex_colordict)
print([cell.face_vertices(fkey) for fkey in cell.faces()])

# pause
rs.EnableRedraw(True)
rs.GetString('Zero faces are shown in red ... Press Enter to arearise cell faces ...')


# ------------------------------------------------------------------------------
#   4. arearise cell faces
# ------------------------------------------------------------------------------
# conduit
conduit = MeshConduit(cell)


def callback(cell, k, args):
    print('iteration times', k)
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

# clean the EGI and cell data
egiartist.clear()
cellartist.clear()
print(lines)
print('egi', egi_arcs)
rs.HideObject(egi_arcs)   # CANNOT HIDE??!!
print(rs.HideObject(egi_arcs))

# planarise cell faces
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
# hide external force vectors
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

print([cell.face_vertices(fkey) for fkey in cell.faces()])
for key in cell.vertices():
    print(cell.vertex_coordinates(key))
    
# draw cell geometry
cellartist.draw_vertices()
#for fkey in target_areas:
#    if target_areas[fkey] != 0:
#        cellartist.draw_faces(keys=[fkey])

import compas.geometry as cg
for fkey in target_areas:
    if target_areas[fkey] != 0:
        # delete duplicate vertex in the face
        original_fkeys =cell.face_vertices(fkey)
        for i, key in enumerate(cell.face_vertices(fkey)):
            key_pre = cell.face_vertices(fkey)[i-1]
            coor_pre = cell.vertex_coordinates(key_pre)
            coor_now = cell.vertex_coordinates(key)
            if cg.distance_point_point(coor_pre, coor_now) == 0:
                del original_fkeys[i]
        cellartist.draw_faces(keys=[fkey])