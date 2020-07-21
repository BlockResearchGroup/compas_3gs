from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.utilities import i_to_red

from compas_rhino.utilities import mesh_from_surface

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.rhino import MeshConduit

from compas_3gs.diagrams import Cell

from compas_3gs.utilities import cell_face_flatness
from compas_3gs.utilities import compare_initial_current

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make cell from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'cell'

guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
rs.HideObjects(guid)

cell = mesh_from_surface(Cell, guid)


# ------------------------------------------------------------------------------
# 2. planarise
# ------------------------------------------------------------------------------

initial_flatness = cell_face_flatness(cell)


# conduit
conduit = MeshConduit(cell)


def callback(cell, k, args):
    current_flatness = cell_face_flatness(cell)
    face_colordict   = compare_initial_current(current_flatness,
                                               initial_flatness,
                                               color_scheme=i_to_red)
    conduit.face_colordict = face_colordict
    conduit.redraw()


with conduit.enabled():
    volmesh_planarise(cell,
                   kmax=1000,
                   callback=callback,
                   print_result_info=True)


# update / redraw
cell.draw()
