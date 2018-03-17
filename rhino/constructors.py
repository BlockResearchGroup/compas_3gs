from __future__ import print_function

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino

from compas.datastructures import Mesh

from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces
from compas_rhino.helpers.mesh import mesh_from_surface

from compas_3gs.datastructures.forcediagram import ForceVM
from compas_3gs.datastructures.formdiagram import FormNW
from compas_3gs.datastructures.formdiagram import FormVM

from compas_3gs.algorithms import volmesh_dual

from compas_rhino.helpers.artists.meshartist import MeshArtist


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   3D GS
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# ==============================================================================
#   3D - force polyhedra as volmesh
# ==============================================================================
def ForceVM_from_polysurfaces():

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)
    forcepolyhedra = ForceVM()
    forcepolyhedra = volmesh_from_polysurfaces(forcepolyhedra, guids)
    forcepolyhedra.attributes['name'] = 'force_volmesh'
    forcepolyhedra.update_data()

    # print("cell", forcepolyhedra.cell)
    # print("halfface", forcepolyhedra.halfface)
    # print("edge", forcepolyhedra.edge)
    # print("vertex", forcepolyhedra.vertex)
    # print("plane", forcepolyhedra.plane)
    # print("halfedge", forcepolyhedra.halfedge)

    rs.AddLayer(name='forcepolyhedra', color=(255, 255, 255))
    forcepolyhedra.draw(layer='forcepolyhedra')
    # forcepolyhedra.draw_vertexlabels()
    # forcepolyhedra.draw_facelabels()
    # forcepolyhedra.draw_edgelabels()
    return forcepolyhedra


# ==============================================================================
#   3D - form diagram as network
# ==============================================================================
def FormNW_from_ForceVM(forcepolyhedra):

    formnetwork = FormNW()
    for ckey in forcepolyhedra.cell:
        x, y, z = forcepolyhedra.cell_centroid(ckey)
        formnetwork.add_vertex(key=ckey, x=x, y=y, z=z)
        for nbr in forcepolyhedra.cell_neighbours(ckey):
            if nbr in formnetwork.edge[ckey]:
                continue
            if nbr in formnetwork.edge and ckey in formnetwork.edge[nbr]:
                continue
            formnetwork.add_edge(ckey, nbr)

    formnetwork.update_data()
    rs.AddLayer(name='formnetwork', color=(0, 0, 0))
    formnetwork.draw(layer='formnetwork')

    return formnetwork


def FormVM_from_ForceVM(forcepolyhedra):
    formvolmesh = volmesh_dual(forcepolyhedra)
    rs.AddLayer(name='formvolmesh', color=(0, 0, 0))

    if formvolmesh:
        formvolmesh.draw(layer='formvolmesh')
        return formvolmesh


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   3D GS
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

def cell_as_mesh():

    guid = rs.GetObjects("select polysurfaces")
    rs.HideObjects(guid)

    cell = Mesh()
    cell = mesh_from_surface(cell, guid)

    rs.AddLayer(name='mesh', color=(0, 0, 0))
    artist = MeshArtist(cell, layer="mesh")

    artist.draw_vertexlabels()
    artist.draw_facelabels()
    artist.draw_edgelabels()

    return cell


def cell_mesh_from_volmesh():

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)
    volmesh = ForceVM()
    volmesh = volmesh_from_polysurfaces(volmesh, guids)
    volmesh.update_data()

    vertices = []
    for vkey in volmesh.vertex:
        vertices.append(volmesh.vertex_coordinates(vkey))

    faces = []
    for fkey in volmesh.faces():
        face = [vkey for vkey in volmesh.halfface_vertices(fkey, ordered=True)]
        faces.append(face)

    cell = Mesh()
    cell = cell.from_vertices_and_faces(vertices, faces)

    rs.AddLayer(name='mesh', color=(0, 0, 0))
    artist = MeshArtist(cell, layer="mesh")

    print('vertex', cell.vertex)
    print('edge', cell.edge)
    print('face', cell.face)
    print('halfedge', cell.halfedge)
    print('facedata', cell.facedata)


    artist.draw_faces()
    artist.draw_edges()
    artist.draw_vertexlabels()
    artist.draw_facelabels()
    artist.draw_edgelabels()

    return cell
