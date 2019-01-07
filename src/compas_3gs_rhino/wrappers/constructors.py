from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import System.Drawing.Color
from System.Drawing.Color import FromArgb

import compas
import compas_rhino

from compas.datastructures import Mesh

from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors




from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import volmesh_from_polysurfaces

from compas_3gs.diagrams import EGI
from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh

from compas_3gs.algorithms import egi_from_vectors
from compas_3gs.algorithms import unit_polyhedron

from compas_3gs.algorithms import volmesh_dual_volmesh
from compas_3gs.algorithms import volmesh_dual_network



from compas_3gs.utilities import resultant_vector


from compas_3gs_rhino.control import get_target_point


try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()


from Rhino.Geometry import Point3d
from Rhino.Geometry import Arc
from Rhino.Geometry import ArcCurve
from Rhino.Geometry import Sphere
from Rhino.Geometry import Vector3d
from Rhino.Geometry import Plane
from Rhino.Geometry import Brep
from Rhino.Geometry import Line


feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
arrow_color    = System.Drawing.Color.FromArgb(255, 0, 79)
jl_blue        = System.Drawing.Color.FromArgb(0, 113, 188)
black          = System.Drawing.Color.FromArgb(0, 0, 0)
gray           = System.Drawing.Color.FromArgb(200, 200, 200)
green          = System.Drawing.Color.FromArgb(0, 255, 0)
white          = System.Drawing.Color.FromArgb(255, 255, 255)


__all__ = [
    'rhino_gfp_from_vectors',
    'rhino_volmesh_from_polysurfaces',
    'rhino_network_from_volmesh',
    'rhino_volmesh_dual_volmesh',
    'rhino_egi_from_volmesh'
]


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# single polyhedral cells
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

def rhino_gfp_from_vectors():
    """Construct a global force polyhedron (gfp) from a set of equilibrated force vectors.

    Returns
    -------
    GFP
        A global force polyhedron as a cell (mesh) object.


    """

    # --------------------------------------------------------------------------
    #   select lines and points
    # --------------------------------------------------------------------------
    guids   = rs.GetObjects("pick lines and points")

    lines   = []
    rxn_pts = []

    for guid in guids:
        if rs.IsCurve(guid):
            lines.append(guid)
        elif rs.IsPoint(guid):
            rxn_pts.append(rs.PointCoordinates(guid))

    # --------------------------------------------------------------------------
    #   compute resultant
    # --------------------------------------------------------------------------
    load_vectors   = {}
    load_locations = {}

    for index, line in enumerate(lines):
        sp = rs.CurveStartPoint(line)
        ep = rs.CurveEndPoint(line)
        load_vectors[index]   = subtract_vectors(ep, sp)
        load_locations[index] = ep

    resultant_xyz, resultant_force = resultant_vector(load_vectors, load_locations)

    # --------------------------------------------------------------------------
    #   pick point  >>>  reaction force vectors
    # --------------------------------------------------------------------------
    def OnDynamicDraw(sender, e):
        cp = e.CurrentPoint
        e.Display.DrawPoint(cp, 0, 3, black)
        axis_sp = add_vectors(resultant_xyz,
                              scale_vector(resultant_force, -10))
        axis_ep = add_vectors(resultant_xyz,
                              scale_vector(resultant_force, 10))
        e.Display.DrawDottedLine(Point3d(*axis_sp),
                                 Point3d(*axis_ep),
                                 feedback_color)
        for sp in rxn_pts:
            e.Display.DrawPoint(sp, 0, 3, black)
            e.Display.DrawLine(sp, cp, black, 2)

    ip   = Point3d(*resultant_xyz)
    line = Rhino.Geometry.Line(ip, ip + Vector3d(*resultant_force))
    gp   = get_target_point(line, OnDynamicDraw)

    rxn_vectors = {}
    for sp in rxn_pts:
        vector = subtract_vectors(gp, sp)
        rxn_vectors[max(int(x) for x in load_vectors.keys()) + 1] = vector

    # --------------------------------------------------------------------------
    #   construct egi
    # --------------------------------------------------------------------------
    force_vectors = load_vectors.copy()
    force_vectors.update(rxn_vectors)

    egi = egi_from_vectors(force_vectors, gp)

    # --------------------------------------------------------------------------
    #   unit polyhedron
    # --------------------------------------------------------------------------
    cell = unit_polyhedron(egi)




    # target areas



    # arearise



    egi.draw()
    cell.draw()

    return egi













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


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
# multi-cell polyhedrons
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


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
