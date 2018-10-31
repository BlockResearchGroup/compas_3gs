from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.datastructures import Mesh

from compas.geometry import distance_point_point

from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.datastructures import VolMesh3gs
from compas_3gs.datastructures import EGI

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network


try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


__all__ = [
    'make_volmesh_from_polysurfaces',
    'make_network_from_volmesh',
    'make_volmesh_dual_volmesh',
    'make_egi_from_volmesh'
]


# ==============================================================================
# single polyhedral cells
# ==============================================================================


def make_gfp_from_vectors():
    pass


def make_egi_from_volmesh(volmesh):
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


def make_volmesh_from_polysurfaces():
    """Construct a volmesh from Rhino polysurfaces.

    Returns
    -------
    Volmesh
        a volmesh object.

    """

    layer = 'force_volmesh'

    # 1. get rhino polysurfaces
    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    # 2. make volmesh
    volmesh       = VolMesh3gs()
    volmesh       = volmesh_from_polysurfaces(volmesh, guids)
    volmesh.layer = layer
    volmesh.attributes['name'] = layer
    volmesh.draw(layer=layer)

    return volmesh


def make_network_from_volmesh(volmesh):
    """Construct a dual network from a volmesh object.

    Parameters
    ----------
    Volmesh
        A volmesh object.

    Returns
    -------
    Network
        A network object.

    """

    layer = 'form_network'

    # 1. make dual network
    network       = volmesh_dual_network(volmesh)
    network.layer = layer
    network.attributes['name'] = layer

    # 2. move network
    x = {vkey: volmesh.vertex_coordinates(vkey)[0] for vkey in volmesh.vertex}
    sorted_x = sorted(x, key=x.get)
    move     = abs(x[sorted_x[0]] - x[sorted_x[-1]])
    for vkey in network.vertex:
        network.vertex[vkey]['x'] += move * 1.25

    network.draw(layer=layer)

    return network


def make_volmesh_dual_volmesh(volmesh):

    layer = 'form_volMesh'

    volmesh = volmesh_dual_volmesh(volmesh)

    if volmesh:
        volmesh.attributes['name'] = layer
        volmesh.initialize_data()
        volmesh.draw(layer=layer)

        return volmesh


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
