from __future__ import print_function

import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino

from compas_rhino.helpers.volmesh import volmesh_from_polysurfaces

from compas_3gs.datastructures.forcediagram import ForceVM
from compas_3gs.datastructures.formdiagram import FormNW
from compas_3gs.datastructures.formdiagram import FormVM

from compas_3gs.algorithms import volmesh_dual


# ==============================================================================
#   FORCE
# ==============================================================================
def ForceVM_from_polysurfaces():

    guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
    rs.HideObjects(guids)
    forcepolyhedra = ForceVM()
    forcepolyhedra = volmesh_from_polysurfaces(forcepolyhedra, guids)
    forcepolyhedra.update_data()

    rs.AddLayer(name='forcepolyhedra', color=(255, 255, 255))
    forcepolyhedra.draw(layer='forcepolyhedra')
    return forcepolyhedra


# ==============================================================================
#   FORM
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
