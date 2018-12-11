from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from System.Drawing import Color
from System.Drawing.Color import FromArgb

import compas
import compas_rhino
import compas_3gs

from compas.utilities import i_to_rgb
from compas.utilities import i_to_red

from compas_rhino.artists import VolMeshArtist
from compas_rhino.artists import NetworkArtist

from compas_rhino.conduits import Conduit

try:
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    compas.raise_if_ironpython()

from Rhino.Geometry import Point3d
from Rhino.Geometry import Line


find_object    = sc.doc.Objects.Find
feedback_color = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor

arrow_color = FromArgb(255, 0, 79)
jl_blue     = FromArgb(0, 113, 188)
black       = FromArgb(0, 0, 0)
gray        = FromArgb(200, 200, 200)
green       = FromArgb(0, 255, 0)
white       = FromArgb(255, 255, 255)

form_color  = Color.FromArgb(255, 255, 255)
force_color = Color.FromArgb(0, 0, 0)


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'PlanarisationConduit',
    # 'ArearisationConduit',
    'MeshArearisationConduit',
    'ReciprocationConduit']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   planarisation conduit
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class PlanarisationConduit(Conduit):

    def __init__(self, volmesh, draw_faces=False, **kwargs):
        super(PlanarisationConduit, self).__init__(**kwargs)

        self.volmesh     = volmesh
        self.draw_faces  = draw_faces
        self.face_colors = {}

    def DrawForeground(self, e):
        _conduit_volmesh(self.volmesh, e)

        if self.face_colors:
            max_value = max(self.face_colors.values())
            for fkey in self.face_colors:
                value     = round(self.face_colors[fkey], 3) / max_value
                color     = FromArgb(*i_to_rgb(value))
                f_vkeys = self.volmesh.halfface_vertices(fkey)
                points   = [self.volmesh.vertex_coordinates(vkey) for vkey in f_vkeys]
                points.append(points[0])
                points   = [Point3d(*pt) for pt in points]
                e.Display.DrawPolygon(points, color, filled=True)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   arearisation conduit
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# class ArearisationConduit(Conduit):

#     def __init__(self,
#                  volmesh,
#                  target_areas_dict,
#                  **kwargs):
#         super(ArearisationConduit, self).__init__(**kwargs)

#         self.volmesh           = volmesh
#         self.target_areas_dict = target_areas_dict

#     def DrawForeground(self, e):

#         deviations = {}
#         for hfkey in self.target_areas_dict:
#             current_area      = self.volmesh.halfface_area(hfkey)
#             target_area       = self.target_areas_dict[hfkey]
#             deviations[hfkey] = abs(current_area - target_area)
#         max_deviation = max(deviations.values())

#         for u, v in self.volmesh.edges_iter():
#             sp  = self.volmesh.vertex_coordinates(u)
#             ep  = self.volmesh.vertex_coordinates(v)
#             e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)

#         for hfkey in self.target_areas_dict:
#             value    = round(deviations[hfkey], 2) / max_deviation
#             color    = FromArgb(*i_to_red(value))
#             area     = self.volmesh.halfface_area(hfkey)
#             center   = self.volmesh.halfface_center(hfkey)
#             hf_vkeys = self.volmesh.halfface_vertices(hfkey)
#             points   = [self.volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
#             points.append(points[0])
#             points   = [Point3d(*pt) for pt in points]
#             e.Display.DrawPolygon(points, color, filled=True)
#             e.Display.DrawDot(Point3d(*center), str(round(area, 3)), color, black)


class MeshArearisationConduit(Conduit):

    def __init__(self, mesh, target_areas_dict, **kwargs):
        super(MeshArearisationConduit, self).__init__(**kwargs)

        self.mesh              = mesh
        self.target_areas_dict = target_areas_dict

    def DrawForeground(self, e):

        deviations = {}
        for hfkey in self.target_areas_dict:
            current_area      = self.mesh.face_area(hfkey)
            target_area       = self.target_areas_dict[hfkey]
            deviations[hfkey] = abs(current_area - target_area)
        max_deviation = max(deviations.values())

        for u, v in self.mesh.edges():
            sp  = self.mesh.vertex_coordinates(u)
            ep  = self.mesh.vertex_coordinates(v)
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)

        for hfkey in self.target_areas_dict:
            value    = round(deviations[hfkey], 2) / max_deviation
            color    = FromArgb(*i_to_red(value))
            area     = self.mesh.face_area(hfkey)
            center   = self.mesh.face_center(hfkey)
            hf_vkeys = self.mesh.face[hfkey]
            points   = [self.mesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            points.append(points[0])
            points   = [Point3d(*pt) for pt in points]
            e.Display.DrawPolygon(points, color, filled=True)
            e.Display.DrawDot(Point3d(*center), str(round(area, 3)), color, black)


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

    def __init__(self, volmesh, network, **kwargs):
        super(ReciprocationConduit, self).__init__(**kwargs)
        self.volmesh = volmesh
        self.network = network

    def DrawForeground(self, e):
        _conduit_volmesh(self.volmesh, e)
        _conduit_network(self.network, e)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   conduit helpers
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def _conduit_network(network, e):
    form_color = Color.FromArgb(255, 255, 255)
    for u, v in network.edges():
        sp  = network.vertex_coordinates(u)
        ep  = network.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 2, form_color)
        e.Display.DrawPoint(Point3d(*ep), 0, 2, form_color)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), form_color, 1)


def _conduit_volmesh(volmesh, e):
    force_color = Color.FromArgb(0, 0, 0)
    for u, v in volmesh.edges():
        sp  = volmesh.vertex_coordinates(u)
        ep  = volmesh.vertex_coordinates(v)
        e.Display.DrawPoint(Point3d(*sp), 0, 2, force_color)
        e.Display.DrawPoint(Point3d(*ep), 0, 2, force_color)
        e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), force_color, 1)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
