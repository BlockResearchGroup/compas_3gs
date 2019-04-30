from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import centroid_polyhedron

from compas_3gs.datastructures import Mesh3gs
from compas_3gs.diagrams import EGI


__all__ = ['Cell']


class Cell(Mesh3gs):
    """A single polyhedral cell, represented as a mesh object.

    """

    def __init__(self):
        super(Cell, self).__init__()

        self.cell = Mesh3gs()
        self.egi  = Mesh3gs()


        a  = {}
        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False}
        ea = {'target_vector': None,
              'target_length': None}
        fa = {'target_area'  : None,
              'target_normal': None}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)
        self.default_face_attributes.update(fa)

    # --------------------------------------------------------------------------
    # misc
    # --------------------------------------------------------------------------

    def cell_center(self):
        vertices = [self.vertex_coordinates(vkey) for vkey in self.vertex]
        return centroid_polyhedron(vertices, self.face)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
