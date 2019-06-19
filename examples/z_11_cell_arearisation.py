from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas.utilities import i_to_blue

from compas_rhino.artists import MeshArtist

from compas_rhino.helpers import mesh_from_surface
from compas_rhino.helpers import mesh_select_face
from compas_rhino.helpers import mesh_select_faces

from compas_3gs.algorithms import mesh_planarise

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

while True:

    cell.draw()

    rs.EnableRedraw(True)

    # --------------------------------------------------------------------------

    option = rs.GetString('Arearise cell',
                          strings=['single',
                                   'multiple',
                                   'exit'])


    if option is None or option == 'exit':
        break

    # arearise a single face ---------------------------------------------------
    if option =='single':
        fkey = mesh_select_face(cell)






    # arearise multiple faces --------------------------------------------------
    if option == 'multiple':

        target_areas = {}

        while True:

            pick = rs.GetString('Set target area',
                                strings=['pick_face',
                                         'exit'])

            if pick == 'pick_face':
                fkey = mesh_select_face(cell)
                target_area = rs.GetReal('set target area', 1, 0.1, 1000.0)
                target_areas[fkey] = target_area

            elif pick == 'exit':
                break

            artist = MeshArtist(cell)
            artist.draw_facelabels(text=target_areas)

            rs.EnableRedraw(True)

        # arearisation options -------------------------------------------------
        fix_normal = rs.GetBoolean('Fix face normals?',
                                   items=[('fix_normals', 'no', 'yes')],
                                   defaults=[False])

        target_normals = {}

        if fix_normal:
            for fkey in cell.faces():
                target_normals[fkey] = cell.face_normal(fkey)

        # arearise -------------------------------------------------------------
        initial_flatness = cell_face_flatness(cell)

        conduit = MeshConduit(cell)

        def callback(cell, k, args):
            current_flatness = cell_face_flatness(cell)
            face_colordict   = compare_initial_current(current_flatness,
                                                       initial_flatness,
                                                       color_scheme=i_to_blue)
            conduit.face_colordict = face_colordict
            conduit.redraw()

        with conduit.enabled():
            mesh_planarise(cell,
                           kmax=500,
                           target_normals=target_normals,
                           target_areas=target_areas,
                           callback=callback)

    # --------------------------------------------------------------------------

    rs.EnableRedraw(True)

rs.EnableRedraw(False)
cell.draw()
