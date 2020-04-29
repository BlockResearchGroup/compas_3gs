from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from copy import deepcopy

from compas.datastructures import Mesh

from compas.datastructures import mesh_split_face

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import cross_vectors

from compas_rhino.artists import MeshArtist

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented
from compas_3gs.utilities import datastructure_centroid


__author__     = 'Juney Lee'
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['Mesh3gs',
            'Mesh3gsArtist',]


class Mesh3gs(Mesh):
    """Inherits and extends the compas Mesh class, such that it is more suitable for 3D graphic statics applications.

    Primarily used for the EGI.

    """

    def __init__(self):
        super(Mesh3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   inherited
    # --------------------------------------------------------------------------

    mesh_split_face        = mesh_split_face
    datastructure_centroid = datastructure_centroid

    def add_edge(self, u, v, attr_dict=None, **kwattr):

        attr = deepcopy(self.default_edge_attributes)
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)

        if u not in self.vertex:
            u = self.add_vertex(u)
        if v not in self.vertex:
            v = self.add_vertex(v)

        data = self.edge[u].get(v, {})
        data.update(attr)

        self.edge[u][v] = data
        if v not in self.halfedge[u]:
            self.halfedge[u][v] = None
        if u not in self.halfedge[v]:
            self.halfedge[v][u] = None

        return u, v

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, vkey, xyz, constrained=True):
        if constrained:
            # X
            if self.vertex[vkey]['x_fix'] is False:
                self.vertex[vkey]['x'] = xyz[0]
            # Y
            if self.vertex[vkey]['y_fix'] is False:
                self.vertex[vkey]['y'] = xyz[1]
            # Z
            if self.vertex[vkey]['z_fix'] is False:
                self.vertex[vkey]['z'] = xyz[2]
        else:
            self.vertex[vkey]['x'] = xyz[0]
            self.vertex[vkey]['y'] = xyz[1]
            self.vertex[vkey]['z'] = xyz[2]

    # --------------------------------------------------------------------------
    # helpers - faces
    # --------------------------------------------------------------------------

    def face_area(self, fkey):
        points = self.face_coordinates(fkey)
        area   = polygon_area_oriented(points)
        return area

    def face_normal(self, fkey, unitized=True):
        points = self.face_coordinates(fkey)
        normal = polygon_normal_oriented(points, unitized)
        if length_vector(normal) == 0 :
            uv     = subtract_vectors(points[1], points[0])
            vw     = subtract_vectors(points[2], points[1])
            normal = normalize_vector(cross_vectors(uv, vw))
        return normal


class Mesh3gsArtist(MeshArtist):
    """Inherits the compas :class:`MeshArtist`, provides functionality for visualisation of 3D graphic statics applications.

    """
    def __init__(self, cell, layer=None):
        super(Mesh3gsArtist, self).__init__(cell, layer=layer)


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
