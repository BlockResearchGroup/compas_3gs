from System.Drawing import Color

import Rhino
from Rhino.Geometry import Point3d
from Rhino.Geometry import Line

from compas_rhino.helpers.artists.volmeshartist import VolMeshArtist
from compas_rhino.helpers.artists import NetworkArtist


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


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
