from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.datastructures import Mesh

from compas.geometry import distance_point_point

from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import EGI
from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__all__ = [
    'rhino_volmesh_from_polysurfaces',
    'rhino_network_from_volmesh',
    'rhino_volmesh_dual_volmesh',
    'rhino_egi_from_volmesh'
]


# ==============================================================================
# single polyhedral cells
# ==============================================================================


def rhino_gfp_from_vectors():
    """Construct a global force polyhedron (gfp) from a set of equilibrated force vectors.

    Returns
    -------
    GFP
        A global force polyhedron as a cell (mesh) object.


    """
    pass


def rhino_egi_from_volmesh(volmesh):
    """Construct an egi for each cell of a volmesh and store it in volmesh.celldata

    Parameters
    ----------
    Volmesh
        A volmesh object.

    Returns
    -------
    Volmesh
        Updated volmesh object.

    """

    for ckey in volmesh.cell:
        egi = EGI()
        egi = egi.from_volmesh_cell(ckey, volmesh)
        egi.attributes['name']        = str(ckey)
        volmesh.celldata[ckey]['egi'] = egi

    return volmesh


# ==============================================================================
# multi-cell polyhedrons
# ==============================================================================


def rhino_volmesh_from_polysurfaces():
    """Construct a volmesh from Rhino polysurfaces.

    Returns
    -------
    Volmesh
        A volmesh object.

    """

    layer = 'force_volmesh'

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    volmesh       = ForceVolMesh()
    volmesh       = volmesh_from_polysurfaces(volmesh, guids)
    volmesh.layer = layer
    volmesh.attributes['name'] = layer
    volmesh.draw(layer=layer)

    return volmesh


def rhino_network_from_volmesh(volmesh, offset=2):
    """Construct a dual network from a volmesh object.

    Parameters
    ----------
    Volmesh
        A volmesh object.
    offset : a float
        Amount to move the form diagram from the force diagram.

    Returns
    -------
    Network
        The dual network object.

    """

    layer = 'form_network'

    network       = volmesh_dual_network(volmesh, cls=FormNetwork)
    network.layer = layer
    network.attributes['name'] = layer

    x_move = network.bounding_box()[0] * offset
    for vkey in network.vertex:
        network.vertex[vkey]['x'] += x_move

    network.draw(layer=layer)

    return network


def rhino_volmesh_dual_volmesh(volmesh):
    """Construct a dual volmesh from a volmesh object.

    Parameters
    ----------
    Volmesh
        A volmesh object.

    Returns
    -------
    Volmesh
        The dual volmesh object.

    """

    layer   = 'form_volmesh'

    volmesh = volmesh_dual_volmesh(volmesh)

    if volmesh:
        volmesh.attributes['name'] = layer
        volmesh.draw(layer=layer)

        return volmesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass





# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   other
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# def cell_as_mesh():

#     guid = rs.GetObjects("select polysurfaces")
#     rs.HideObjects(guid)

#     cell = Mesh()
#     cell = mesh_from_surface(cell, guid)

#     rs.AddLayer(name='mesh', color=(0, 0, 0))
#     artist = MeshArtist(cell, layer="mesh")

#     artist.draw_vertexlabels()
#     artist.draw_facelabels()
#     artist.draw_edgelabels()

#     return cell


# def cell_mesh_from_volmesh():

#     guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
#     rs.HideObjects(guids)
#     volmesh = ForceVolMesh()
#     volmesh = volmesh_from_polysurfaces(volmesh, guids)
#     volmesh.update_data()

#     vertices = []
#     for vkey in volmesh.vertex:
#         vertices.append(volmesh.vertex_coordinates(vkey))

#     faces = []
#     for fkey in volmesh.faces():
#         face = [vkey for vkey in volmesh.halfface_vertices(fkey, ordered=True)]
#         faces.append(face)

#     cell = Mesh()
#     cell = cell.from_vertices_and_faces(vertices, faces)

#     rs.AddLayer(name='mesh', color=(0, 0, 0))
#     artist = MeshArtist(cell, layer="mesh")

#     print('vertex', cell.vertex)
#     print('edge', cell.edge)
#     print('face', cell.face)
#     print('halfedge', cell.halfedge)
#     print('facedata', cell.facedata)


#     artist.draw_faces()
#     artist.draw_edges()
#     artist.draw_vertexlabels()
#     artist.draw_facelabels()
#     artist.draw_edgelabels()

#     return cell
