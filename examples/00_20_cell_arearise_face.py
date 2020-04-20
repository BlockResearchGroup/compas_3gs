from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time

import compas
from compas.geometry import dot_vectors
from compas.utilities import i_to_blue

from compas_rhino.geometry._constructors import mesh_from_surface
from compas_rhino.selectors import mesh_select_face

from compas_3gs.algorithms import cell_arearise_face
from compas_3gs.diagrams import Cell
from compas_3gs.operations import cell_relocate_face
from compas_3gs.rhino import MeshConduit

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
#   1. make cell from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'cell'  # unused variable

guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
cell = mesh_from_surface(Cell, guid)
cell.draw()
rs.HideObjects(guid)

# ------------------------------------------------------------------------------
#   2. Target area
# ------------------------------------------------------------------------------
fkey   = mesh_select_face(cell)
area   = cell.face_area(fkey)
center = cell.face_centroid(fkey)
normal = cell.face_normal(fkey)

target_area = rs.GetReal("Enter target area", number=area)
# ------------------------------------------------------------------------------
#   3. Arearise cell face
# ------------------------------------------------------------------------------

# conduit
conduit = MeshConduit(cell)

    
def callback(cell, args):

    current_area = cell.face_area(fkey)
    color  = i_to_blue(abs(current_area - target_area) / target_area)
    conduit.face_colordict = {fkey: color}

    time.sleep(0.05)

    conduit.redraw()

with conduit.enabled():
    cell_arearise_face(cell,
                       fkey,
                       target_area,
                       callback=callback)

# ------------------------------------------------------------------------------
#   4. Check result
# ------------------------------------------------------------------------------
new_area   = cell.face_area(fkey)
new_normal = cell.face_normal(fkey)
if dot_vectors(normal, new_normal) < 0:
    new_area *= -1

if abs(new_area - target_area) > 1:

    print('===================================================================')
    print('')
    print('Arearisation attempted, but did not converge...')
    print('It is likely that the target area is not valid / inexistent...')
    print('')
    print('===================================================================')

    cell_relocate_face(cell, fkey, center, normal)

# ------------------------------------------------------------------------------
#   5. Draw result
# ------------------------------------------------------------------------------
cell.draw()
