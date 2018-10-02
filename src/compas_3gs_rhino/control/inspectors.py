import System.Drawing.Color

from compas_rhino.conduits import Conduit
from compas_rhino.ui.mouse import Mouse

from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors

from compas.utilities import i_to_rgb

try:
    from Rhino.Geometry import Point3d

    from System.Drawing.Color import FromArgb

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


__all__ = ['VolmeshVertexInspector',
           'VolmeshHalffaceInspector',
           'VolmeshCellInspector',
           'BiCellInspector']


# ==============================================================================
#   volmesh vetex
# ==============================================================================

class VolmeshVertexInspector(Conduit):

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



# ==============================================================================
#   volmesh halfface
# ==============================================================================

class VolmeshHalffaceInspector(Conduit):

    def __init__(self, volmesh, hfkeys=None, dependents=False, tol=1, **kwargs):
        super(VolmeshHalffaceInspector, self).__init__(**kwargs)

        dotcolor       = (0, 0, 0)
        textcolor      = (255, 255, 255)
        edgecolor      = (255, 255, 0)
        facecolor      = (255, 0, 0)

        self.volmesh   = volmesh
        self.hfkeys    = hfkeys
        self.dependents = dependents
        self.tol       = tol
        self.mouse     = Mouse()
        self.dotcolor  = FromArgb(*dotcolor)
        self.textcolor = FromArgb(*textcolor)
        self.edgecolor = FromArgb(*edgecolor)
        self.facecolor = FromArgb(*facecolor)

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

        hfkeys = self.volmesh.halfface.keys()
        if self.hfkeys:
            hfkeys = self.hfkeys

        # force diagram
        for hfkey in hfkeys:

            p0  = self.volmesh.halfface_center(hfkey)
            v01 = subtract_vectors(p1, p0)
            v02 = subtract_vectors(p2, p0)
            l   = length_vector(cross_vectors(v01, v02))

            dep_hfkeys = self.volmesh.volmesh_all_dependent_halffaces(hfkey)

            if l12 == 0.0 or (l / l12) < self.tol:

                vkeys = self.volmesh.halfface_vertices(hfkey)
                face_coordinates = [self.volmesh.vertex_coordinates(vkey) for vkey in vkeys]
                face_coordinates.append(face_coordinates[0])
                polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                e.Display.DrawPolyline(polygon_xyz, self.edgecolor, 4)

                if self.dependents:
                    for key in dep_hfkeys:
                        vkeys = self.volmesh.halfface_vertices(key)
                        face_coordinates = [self.volmesh.vertex_coordinates(vkey) for vkey in vkeys]
                        face_coordinates.append(face_coordinates[0])
                        polygon_xyz = [Point3d(*xyz) for xyz in face_coordinates]
                        e.Display.DrawPolyline(polygon_xyz, self.edgecolor, 2)

                break

# ==============================================================================
#   volmesh cell
# ==============================================================================

class VolmeshCellInspector(Conduit):

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



# ==============================================================================
#   volmesh cell
# ==============================================================================

class BiCellInspector(Conduit):

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

                    hfkey = self.volmesh.cell_pair_hfkeys(ckey, nbr_vkey)[0]
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
