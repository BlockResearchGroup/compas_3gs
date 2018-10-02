from __future__ import print_function

import rhinoscriptsyntax as rs
import Rhino

from compas.datastructures import Mesh

from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

from compas_3gs.datastructures.forcevolmesh import ForceVolMesh
from compas_3gs.datastructures.formnetwork import FormNetwork
from compas_3gs.datastructures.formvolmesh import FormVolMesh
from compas_3gs.datastructures.egi import EGI

from compas.geometry import distance_point_point

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network

from compas_rhino.helpers.artists.meshartist import MeshArtist




__all__ = [
    'forcevolmesh_from_polysurfaces',
    'formnetwork_from_forcevolmesh',
    'formvolmesh_from_forcevolmesh',
    'egi_from_volmesh'
]



# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def forcevolmesh_from_polysurfaces():

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)

    layer = 'forcediagram'

    forcepolyhedra = ForceVolMesh()
    forcepolyhedra = volmesh_from_polysurfaces(forcepolyhedra, guids)
    forcepolyhedra.attributes['name'] = 'ForceVolMesh'
    forcepolyhedra.layer = layer
    forcepolyhedra.initialize_data()

    rs.AddLayer(name=layer, color=(255, 255, 255))
    forcepolyhedra.draw(layer=layer)
    # forcepolyhedra.draw_vertex_labels()
    # forcepolyhedra.draw_face_labels()
    # forcepolyhedra.draw_cell_labels()

    egi_from_volmesh(forcepolyhedra)

    return forcepolyhedra


def formnetwork_from_forcevolmesh(forcepolyhedra):

    layer = 'formdiagram'

    x = {vkey: forcepolyhedra.vertex_coordinates(vkey)[0] for vkey in forcepolyhedra.vertex}
    sorted_x = sorted(x, key=x.get)
    print(sorted_x)


    move = abs(x[sorted_x[0]] - x[sorted_x[-1]])

    rs.AddLayer(name=layer, color=(0, 0, 0))

    formnetwork = volmesh_dual_network(forcepolyhedra)
    formnetwork.attributes['name'] = 'FormNetwork'
    formnetwork.layer = layer
    formnetwork.initialize_data()

    for vkey in formnetwork.vertex:
        formnetwork.vertex[vkey]['x'] += move * 1.25

    formnetwork.draw(layer=layer)

    return formnetwork


def formvolmesh_from_forcevolmesh(forcepolyhedra):

    rs.AddLayer(name='formvolmesh', color=(0, 0, 0))

    formvolmesh = volmesh_dual_volmesh(forcepolyhedra)

    if formvolmesh:

        formvolmesh.attributes['name'] = 'FormVolMesh'
        formvolmesh.initialize_data()
        formvolmesh.draw(layer='formvolmesh')

        return formvolmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   egi
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

def egi_from_volmesh(volmesh):
    for ckey in volmesh.cell:
        egi = EGI()
        egi = egi.from_volmesh_cell(ckey, volmesh)
        egi.attributes['name'] = str(ckey)
        volmesh.c_data[ckey]['egi'] = egi

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
