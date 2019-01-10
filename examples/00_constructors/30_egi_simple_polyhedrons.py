from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.geometry import subtract_vectors

from compas_3gs.algorithms import egi_from_vectors
from compas_3gs.algorithms import unit_polyhedron
from compas_3gs.algorithms import mesh_arearise

from compas_3gs.rhino.display import MeshConduit


try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
#   1. get force vectors
# ------------------------------------------------------------------------------
lines  = rs.GetObjects("pick lines", preselect=True, filter=rs.filter.curve)
origin = rs.GetPoint("pick origin")

vectors      = {}
target_areas = {}
for index, line in enumerate(lines):
    sp  = rs.CurveStartPoint(line)
    ep  = rs.CurveEndPoint(line)
    mag = rs.CurveLength(line)
    vectors[index]      = subtract_vectors(ep, sp)
    target_areas[index] = mag


# ------------------------------------------------------------------------------
#   2. make egi
# ------------------------------------------------------------------------------
egi = egi_from_vectors(vectors, origin)

egi.draw()


# ------------------------------------------------------------------------------
#   3. unit polyhedron
# ------------------------------------------------------------------------------
cell = unit_polyhedron(egi)



# ------------------------------------------------------------------------------
#   3. arearise
# ------------------------------------------------------------------------------
conduit = MeshConduit(cell)

def callback(cell, k, args):
    # if k % 2 == 0:
    conduit.redraw()


# ------------------------------------------------------------------------------
#   3. arearise
# ------------------------------------------------------------------------------

for fkey in cell.face:
    if fkey not in target_areas:
        target_areas[fkey] = 0

# target_normals = {}
# for fkey in cell.face:
#     target_normals[fkey] = egi.vertex[fkey]['normal']



mesh_arearise(cell,
              kmax=5,
              target_areas=target_areas,
              target_normals=target_normals,
              callback=callback)


cell.draw()
