from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_rhino.selectors import VertexSelector

from compas.utilities import i_to_red

from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_planarise

from compas_3gs.rhino import rhino_volmesh_from_polysurfaces
from compas_3gs.rhino import rhino_volmesh_planarise
from compas_3gs.rhino import VolmeshConduit
from compas_3gs.rhino import compare_initial_current


from compas_3gs.utilities import volmesh_face_flatness

try:
    import rhinoscriptsyntax as rs

    from System.Drawing.Color import FromArgb

except ImportError:
    compas.raise_if_ironpython()


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram       = ForceVolMesh()
forcediagram       = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer

forcediagram.draw(layer=layer)


# ------------------------------------------------------------------------------
# 2. pick vertices to fix
# ------------------------------------------------------------------------------
vkeys = VertexSelector.select_vertices(forcediagram,
                                       message='Select vertices to fix:')


# ------------------------------------------------------------------------------
# 3. planarise
# ------------------------------------------------------------------------------
forcediagram.clear()

initial_flatness = volmesh_face_flatness(forcediagram)

# conduit
conduit = VolmeshConduit(forcediagram)

def callback(forcediagram, k, args):
    if k % 2:
        current_flatness = volmesh_face_flatness(forcediagram)
        face_colordict   = compare_initial_current(current_flatness,
                                                   initial_flatness,
                                                   color_scheme=i_to_red)
        conduit.face_colordict = face_colordict
        conduit.redraw()

# planarise
with conduit.enabled():
    volmesh_planarise(forcediagram,
                      kmax=1000,
                      fix_vkeys=vkeys,
                      fix_boundary_normals=False,
                      tolerance_flat=0.001,
                      callback=callback)

# update / redraw
forcediagram.draw()
