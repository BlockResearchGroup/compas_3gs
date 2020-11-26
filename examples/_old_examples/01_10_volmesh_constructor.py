from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh

from compas_rhino.artists import VolMeshArtist


try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()


# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
layer = 'force_volmesh'

guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

forcediagram = ForceVolMesh()
forcediagram = volmesh_from_polysurfaces(forcediagram, guids)
forcediagram.layer = layer
forcediagram.attributes['name'] = layer

artist = VolMeshArtist(forcediagram)

artist.draw_vertices()
artist.draw_faces()
artist.draw_vertexlabels()
