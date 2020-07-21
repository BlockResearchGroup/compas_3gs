from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import time

import compas

from compas_rhino import unload_modules
unload_modules('compas')

from compas.geometry import dot_vectors
from compas.utilities import i_to_blue

from compas_rhino.geometry import RhinoSurface
from compas_rhino.objects.selectors import FaceSelector

from compas_3gs.algorithms import cell_arearise_face
from compas_3gs.diagrams import Cell
from compas_3gs.operations import cell_relocate_face
from compas_3gs.rhino import MeshConduit
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
#   1. make cell from rhino polysurfaces
# ------------------------------------------------------------------------------
# select the polysurface which you create in Rhino
guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
# turn Rhino polysurface to a COMPAS single polyhedral cell
cell = RhinoSurface.from_guid(guid).brep_to_compas(cls=Cell())

# draw the polyhedral cell
layer = 'cell'
cellartist = Mesh3gsArtist(cell, layer=layer)
cellartist.draw()
# hide Rhino polysurface
rs.HideObjects(guid)


# ------------------------------------------------------------------------------
#   2. Target area
# ------------------------------------------------------------------------------
# select a mesh face and get its face key, area, center point and normal vector
fkey   = FaceSelector.select_face(cell)
area   = cell.face_area(fkey)
center = cell.face_centroid(fkey)
normal = cell.face_normal(fkey)

# input target area value, current face area is shown as a reference
target_area = rs.GetReal("Enter target area", number=area)


# ------------------------------------------------------------------------------
#   3. Arearise cell face
# ------------------------------------------------------------------------------
# conduit
conduit = MeshConduit(cell, refreshrate=1)


def callback(cell, args=None):
    current_area = cell.face_area(fkey)
    color  = i_to_blue(abs(current_area - target_area) / target_area)
    conduit.face_colordict = {fkey: color}
    time.sleep(0.05)
    conduit.redraw(k=1)

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

# WHAT IS THIS FOR? NEW AREA SHOULD ANYWAY BE BIGGER THAN 0?
if dot_vectors(normal, new_normal) < 0:
    new_area *= -1

# check whether the arearisation succeed
if abs(new_area - target_area) > 1:
    print('===================================================================')
    print('')
    print('Arearisation attempted, but did not converge...')
    print('It is likely that the target area is not valid / inexistent...')
    print('')
    print('===================================================================')

    # retrieve the origianl mesh face
    cell_relocate_face(cell, fkey, center, normal)


# ------------------------------------------------------------------------------
#   5. Draw result
# ------------------------------------------------------------------------------
new_layer = 'arearised_cell'
new_cellartist = Mesh3gsArtist(cell, layer=new_layer)
new_cellartist.draw()

