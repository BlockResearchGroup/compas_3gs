from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors

from compas.utilities import i_to_rgb

from compas_rhino.conduits import BaseConduit
from compas_rhino.ui import Mouse

try:
    from Rhino.Geometry import Line
    from Rhino.Geometry import Point3d

    from System.Drawing.Color import FromArgb

except ImportError:
    compas.raise_if_ironpython()


__all__ = ['VolmeshVertexInspector',
           'VolmeshHalffaceInspector',
           'VolmeshCellInspector',
           'BiCellInspector']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh vertex inspector
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class VolmeshVertexInspector(BaseConduit):

    def __init__(self, volmesh, tol=0.1, **kwargs):
        super(VolmeshVertexInspector, self).__init__(**kwargs)

        dotcolor       = (255, 0, 0)
        textcolor      = (255, 255, 255)

        self.volmesh   = volmesh
        self.tol       = tol
        self.mouse     = Mouse()
        self.dotcolor  = FromArgb(*dotcolor)
        self.textcolor = FromArgb(*textcolor)

    def enable(self):
        self.mouse.Enabled = True
        self.Enabled = True

    def disable(self):
        self.mouse.Enabled = False
        self.Enabled = False

    def DrawForeground(self, e):
        p1  = self.mouse.p1
        p2  = self.mouse.p2
        v12 = subtract_vectors(p2, p1)
        l12 = length_vector(v12)

        for index, (key, attr) in enumerate(self.volmesh.vertices(True)):
            p0   = attr['x'], attr['y'], attr['z']
            text = str(index)
            v01  = subtract_vectors(p1, p0)
            v02  = subtract_vectors(p2, p0)
            l    = length_vector(cross_vectors(v01, v02))

            if l12 == 0.0 or (l / l12) < self.tol:
                point = Point3d(*p0)
                e.Display.DrawDot(point, text, self.dotcolor, self.textcolor)

                break


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh halfface inspector
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class VolmeshHalffaceInspector(BaseConduit):

    def __init__(self, volmesh, hfkeys=None, dependents=False, tol=1, **kwargs):
        super(VolmeshHalffaceInspector, self).__init__(**kwargs)

        dotcolor        = (0, 0, 0)
        textcolor       = (255, 255, 255)
        edgecolor       = (255, 255, 0)
        facecolor       = (255, 0, 0)

        self.volmesh    = volmesh
        self.hfkeys     = hfkeys
        self.dependents = dependents
        self.tol        = tol
        self.mouse      = Mouse()
        self.dotcolor   = FromArgb(*dotcolor)
        self.textcolor  = FromArgb(*textcolor)
        self.edgecolor  = FromArgb(*edgecolor)
        self.facecolor  = FromArgb(*facecolor)

    def enable(self):
        self.mouse.Enabled = True
        self.Enabled = True

    def disable(self):
        self.mouse.Enabled = False
        self.Enabled = False

    def DrawForeground(self, e):
        p1  = self.mouse.p1
        p2  = self.mouse.p2

        v12 = subtract_vectors(p2, p1)
        l12 = length_vector(v12)

        hfkeys = self.volmesh.faces()
        if self.hfkeys:
            hfkeys = self.hfkeys

        for hfkey in hfkeys:

            p0  = self.volmesh.halfface_center(hfkey)
            v01 = subtract_vectors(p1, p0)
            v02 = subtract_vectors(p2, p0)
            l   = length_vector(cross_vectors(v01, v02))

            if l12 == 0.0 or (l / l12) < self.tol:

                face_coordinates = self.volmesh.halfface_coordinates(hfkey)
                face_coordinates.append(face_coordinates[0])
                polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                e.Display.DrawPolyline(polygon_xyz, self.edgecolor, 6)

                if self.dependents:

                    d_hfkeys = self.volmesh.halfface_manifold_neighborhood(hfkey, ring=50)

                    for d_hfkey in d_hfkeys:
                        face_coordinates = self.volmesh.halfface_coordinates(d_hfkey)
                        face_coordinates.append(face_coordinates[0])
                        polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                        e.Display.DrawPolyline(polygon_xyz, self.edgecolor, 2)

                break


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh cell inspector
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class VolmeshCellInspector(BaseConduit):

    def __init__(self, volmesh, color_dict=None, tol=1, **kwargs):
        super(VolmeshCellInspector, self).__init__(**kwargs)

        dotcolor        = (0, 0, 0)
        textcolor       = (255, 255, 255)
        edgecolor       = (0, 0, 0)
        facecolor       = (255, 0, 0)

        self.volmesh    = volmesh
        self.color_dict = color_dict
        self.tol        = tol
        self.mouse      = Mouse()
        self.dotcolor   = FromArgb(*dotcolor)
        self.textcolor  = FromArgb(*textcolor)
        self.edgecolor  = FromArgb(*edgecolor)
        self.facecolor  = FromArgb(*facecolor)

    def enable(self):
        self.mouse.Enabled = True
        self.Enabled = True

    def disable(self):
        self.mouse.Enabled = False
        self.Enabled = False

    def DrawForeground(self, e):
        p1  = self.mouse.p1
        p2  = self.mouse.p2
        v12 = subtract_vectors(p2, p1)
        l12 = length_vector(v12)

        # force diagram
        for ckey in self.volmesh.cell:
            p0      = self.volmesh.cell_center(ckey)
            v01 = subtract_vectors(p1, p0)
            v02 = subtract_vectors(p2, p0)
            l   = length_vector(cross_vectors(v01, v02))
            color = self.edgecolor
            if self.color_dict:
                color = FromArgb(*self.color_dict[ckey])
            if l12 == 0.0 or (l / l12) < self.tol:
                for hfkey in self.volmesh.cell_halffaces(ckey):
                    vkeys = self.volmesh.halfface_vertices(hfkey)
                    face_coordinates = [self.volmesh.vertex_coordinates(vkey) for vkey in vkeys]
                    face_coordinates.append(face_coordinates[0])
                    polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                    e.Display.DrawPolyline(polygon_xyz, color, 3)
                break


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   volmesh cell - network vertex - inspector
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class BiCellInspector(BaseConduit):

    def __init__(self, volmesh, network, tol=2, **kwargs):
        super(BiCellInspector, self).__init__(**kwargs)

        dotcolor       = (0, 0, 0)
        textcolor      = (255, 255, 255)
        edgecolor      = (0, 0, 0)
        facecolor      = (255, 0, 0)

        self.volmesh   = volmesh
        self.network   = network
        self.tol       = tol
        self.mouse     = Mouse()
        self.dotcolor  = FromArgb(*dotcolor)
        self.textcolor = FromArgb(*textcolor)
        self.edgecolor = FromArgb(*edgecolor)
        self.facecolor = FromArgb(*facecolor)

        # self.color_dict = {}

        # for index, hfkey in self.volmesh.halffaces.keys():
        #     value = index / max(self.volmesh.halffaces.keys())
        #     color  = i_to_rgb(value)
        #     color  = System.Drawing.Color.FromArgb(*color)
        #     self.color_dict[hfkey] = color

    def enable(self):
        self.mouse.Enabled = True
        self.Enabled = True

    def disable(self):
        self.mouse.Enabled = False
        self.Enabled = False

    def DrawForeground(self, e):
        p1  = self.mouse.p1
        p2  = self.mouse.p2
        v12 = subtract_vectors(p2, p1)
        l12 = length_vector(v12)

        # force diagram

        for ckey in self.volmesh.cell:
            p0      = self.volmesh.cell_center(ckey)
            dual_p0 = self.network.vertex_coordinates(ckey)
            v01 = subtract_vectors(p1, p0)
            v02 = subtract_vectors(p2, p0)
            l   = length_vector(cross_vectors(v01, v02))


            if l12 == 0.0 or (l / l12) < self.tol:

                hf_colors = {}

                nbr_vkeys = self.network.vertex_neighbours(ckey)

                for index, nbr_vkey in enumerate(nbr_vkeys):
                    value  = float(index) / (len(nbr_vkeys) - 1)

                    print('boo', value)

                    color  = i_to_rgb(value)
                    color  = System.Drawing.Color.FromArgb(*color)
                    nbr_xyz = self.network.vertex_coordinates(nbr_vkey)
                    e.Display.DrawLine(Point3d(*dual_p0), Point3d(*nbr_xyz), color, 4)

                    hfkey = self.volmesh.cell_pair_halffaces(ckey, nbr_vkey)[0]
                    hf_colors[hfkey] = color



                for hfkey in self.volmesh.cell_halffaces(ckey):
                    vkeys = self.volmesh.halfface_vertices(hfkey)
                    face_coordinates = [self.volmesh.vertex_coordinates(vkey) for vkey in vkeys]
                    face_coordinates.append(face_coordinates[0])
                    polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                    e.Display.DrawDot(Point3d(*p0), str(ckey), self.dotcolor, self.textcolor)
                    e.Display.DrawPolyline(polygon_xyz, self.edgecolor, 2)

                    e.Display.DrawDot(Point3d(*dual_p0), str(ckey), self.dotcolor, self.textcolor)

                    if hfkey in hf_colors:
                        hf_color = hf_colors[hfkey]
                        e.Display.DrawPolygon(polygon_xyz, hf_color, filled=True)

                break


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   Main
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


if __name__ == '__main__':
    pass
