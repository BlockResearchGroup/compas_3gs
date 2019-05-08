from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino.conduits import Conduit

try:
    import Rhino
    import scriptcontext as sc

    from Rhino.Geometry import Point3d
    from Rhino.Geometry import Line

    from System.Drawing.Color import FromArgb

    find_object    = sc.doc.Objects.Find
    feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

    arrow_color = FromArgb(255, 0, 79)
    jl_blue     = FromArgb(0, 113, 188)
    black       = FromArgb(0, 0, 0)
    gray        = FromArgb(200, 200, 200)
    green       = FromArgb(0, 255, 0)
    white       = FromArgb(255, 255, 255)
    form_color  = FromArgb(255, 255, 255)
    force_color = FromArgb(0, 0, 0)

except ImportError:
    compas.raise_if_ironpython()


__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['MeshConduit',
           'VolmeshConduit',
           'ReciprocationConduit']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   mesh conduit
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class MeshConduit(Conduit):
    """Conduit for mesh algorithms.

    """

    def __init__(self, mesh, face_colordict={}, **kwargs):
        super(MeshConduit, self).__init__(**kwargs)

        self.mesh           = mesh
        self.face_colordict = face_colordict

    def DrawForeground(self, e):
        _conduit_mesh_edges(self.mesh, e)

        if self.face_colordict:
            for fkey in self.face_colordict:
                color  = FromArgb(*self.face_colordict[fkey])
                points = self.mesh.face_coordinates(fkey)
                points.append(points[0])
                points  = [Point3d(*pt) for pt in points]
                e.Display.DrawPolygon(points, color, filled=True)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh conduit
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class VolmeshConduit(Conduit):
    """Conduit for volmesh algorithms.

    """

    def __init__(self, volmesh, face_colordict={}, **kwargs):
        super(VolmeshConduit, self).__init__(**kwargs)

        self.volmesh        = volmesh
        self.face_colordict = face_colordict

    def DrawForeground(self, e):
        _conduit_volmesh_edges(self.volmesh, e)

        if self.face_colordict:
            for fkey in self.face_colordict:
                color   = FromArgb(*self.face_colordict[fkey])
                f_vkeys = self.volmesh.halfface_vertices(fkey)
                points  = [self.volmesh.vertex_coordinates(vkey) for vkey in f_vkeys]
                points.append(points[0])
                points = [Point3d(*pt) for pt in points]
                e.Display.DrawPolygon(points, color, filled=True)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   reciprocation conduit
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class ReciprocationConduit(Conduit):
    """Conduit for the reciprocation algorithm.

    """

    def __init__(self, volmesh, network, **kwargs):
        super(ReciprocationConduit, self).__init__(**kwargs)
        self.volmesh = volmesh
        self.network = network

    def DrawForeground(self, e):
        _conduit_volmesh_edges(self.volmesh, e)
        _conduit_network_edges(self.network, e)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   conduit helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _conduit_network_edges(network, e):
    for u, v in network.edges():
        sp = network.vertex_coordinates(u)
        ep = network.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 4, white)
        e.Display.DrawPoint(Point3d(*ep), 0, 4, white)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)


def _conduit_mesh_edges(mesh, e):
    for u, v in mesh.edges():
        sp = mesh.vertex_coordinates(u)
        ep = mesh.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 4, white)
        e.Display.DrawPoint(Point3d(*ep), 0, 4, white)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)


def _conduit_volmesh_edges(volmesh, e):
    for u, v in volmesh.edges():
        sp = volmesh.vertex_coordinates(u)
        ep = volmesh.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 4, white)
        e.Display.DrawPoint(Point3d(*ep), 0, 4, white)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == "__main__":
    pass
