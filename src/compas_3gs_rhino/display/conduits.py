from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import System
from System.Drawing import Color
from System.Drawing.Color import FromArgb

import compas
import compas_rhino
import compas_3gs

from compas.utilities import i_to_rgb
from compas.utilities import i_to_red

from compas_rhino.helpers import VolMeshArtist
from compas_rhino.helpers import NetworkArtist

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
arrow_color    = FromArgb(255, 0, 79)
jl_blue        = FromArgb(0, 113, 188)
black          = FromArgb(0, 0, 0)
gray           = FromArgb(200, 200, 200)
green          = FromArgb(0, 255, 0)
white          = FromArgb(255, 255, 255)


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = [
    'planarisation_conduit',
    'arearisation_conduit',
    'mesh_arearisation_conduit',
    'reciprocation_conduit']


class planarisation_conduit(Rhino.Display.DisplayConduit):

    def __init__(self,
                 volmesh):
        super(planarisation_conduit, self).__init__()

        self.volmesh = volmesh

    def DrawForeground(self, e):
        self.volmesh.clear()
        for u, v in self.volmesh.edges_iter():
            sp  = self.volmesh.vertex_coordinates(u)
            ep  = self.volmesh.vertex_coordinates(v)
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), black, 1)


class arearisation_conduit(Rhino.Display.DisplayConduit):

    def __init__(self,
                 volmesh,
                 target_areas_dict):
        super(arearisation_conduit, self).__init__()

        self.volmesh           = volmesh
        self.target_areas_dict = target_areas_dict

    def DrawForeground(self, e):

        deviations = {}
        for hfkey in self.target_areas_dict:
            current_area      = self.volmesh.halfface_area(hfkey)
            target_area       = self.target_areas_dict[hfkey]
            deviations[hfkey] = abs(current_area - target_area)
        max_deviation = max(deviations.values())

        for u, v in self.volmesh.edges_iter():
            sp  = self.volmesh.vertex_coordinates(u)
            ep  = self.volmesh.vertex_coordinates(v)
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), white, 1)

        for hfkey in self.target_areas_dict:
            value    = round(deviations[hfkey], 2) / max_deviation
            color    = FromArgb(*i_to_red(value))
            area     = self.volmesh.halfface_area(hfkey)
            center   = self.volmesh.halfface_center(hfkey)
            hf_vkeys = self.volmesh.halfface_vertices(hfkey)
            points   = [self.volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
            points.append(points[0])
            points   = [Point3d(*pt) for pt in points]
            e.Display.DrawPolygon(points, color, filled=True)
            e.Display.DrawDot(Point3d(*center), str(round(area, 3)), color, black)




class mesh_arearisation_conduit(Rhino.Display.DisplayConduit):

    def __init__(self,
                 mesh,
                 target_areas_dict):
        super(mesh_arearisation_conduit, self).__init__()

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




class reciprocation_conduit(Rhino.Display.DisplayConduit):
    """ Conduit for brg_algorithms.reciprocate.polyhedra_algorithms.reicprocate_force.
    """

    def __init__(self,
                 volmesh,
                 network):

        super(reciprocation_conduit, self).__init__()

        self.volmesh = volmesh
        self.network = network

    def DrawForeground(self, e):

        artist = VolMeshArtist(self.volmesh)
        artist.clear()

        artist = NetworkArtist(self.network)
        artist.clear()

        # ----------------------------------------------------------------------
        #   form diagram
        # ----------------------------------------------------------------------
        form_color = Color.FromArgb(0, 0, 0)
        for u, v in self.network.edges_iter():
            sp  = self.network.vertex_coordinates(u)
            ep  = self.network.vertex_coordinates(v)
            e.Display.DrawPoint(Point3d(*sp), 0, 4, form_color)
            e.Display.DrawPoint(Point3d(*ep), 0, 4, form_color)
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), form_color, 1)

        # ----------------------------------------------------------------------
        #   force diagram
        # ----------------------------------------------------------------------
        force_color = Color.FromArgb(200, 200, 200)
        for u, v in self.volmesh.edges_iter():
            sp  = self.volmesh.vertex_coordinates(u)
            ep  = self.volmesh.vertex_coordinates(v)
            e.Display.DrawPoint(Point3d(*sp), 0, 4, force_color)
            e.Display.DrawPoint(Point3d(*ep), 0, 4, force_color)
            e.Display.DrawLine(Line(Point3d(*sp), Point3d(*ep)), force_color, 1)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
