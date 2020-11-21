from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import angle_vectors

from compas_3gs.datastructures import Network3gs
from compas_3gs.datastructures import VolMesh3gs


__all__ = ['FormNetwork',
           'ForceVolMesh']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   polyheral form diagram - as network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class FormNetwork(Network3gs):
    """A polyhedral form diagram, represented as a network object.

    """

    __module__ = 'compas_3gs.diagrams'

    def __init__(self):
        super(FormNetwork, self).__init__()
        self.dual = None

        a = {'scale': 1}

        va = {'is_fixed': False,
              'x_fix': False,
              'y_fix': False,
              'z_fix': False}

        ea = {'l_min': 1,
              'l_max': 20,
              'target_vector': None,
              'target_length': None,
              '_a': 0.0}

        self.attributes.update(a)
        self.default_node_attributes.update(va)
        self.default_edge_attributes.update(ea)

    def dual_halfface(self, edge):
        u, v = edge
        u_halfface, v_halfface = self.dual.cell_pair_halffaces(u, v)
        return u_halfface

    def update_angle_deviations(self):
        """Compute the angle deviation with the corresponding halfface normal in the ForceVolMesh.
        """
        for edge in self.edges():
            halfface = self.dual_halfface(edge)
            normal = self.dual.halfface_normal(halfface)
            edge_vector = self.edge_vector(*edge)
            a = angle_vectors(edge_vector, normal, deg=True)
            self.edge_attribute(edge, '_a', a)
            self.dual.face_attribute(halfface, '_a', a)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   polyheral form diagram - as volmesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


# class FormVolMesh(VolMesh3gs):
#     """A polyhedral form diagram, represented as a volmesh object.

#     """

#     __module__ = 'compas_3gs.diagrams'

#     def __init__(self):
#         super(FormVolMesh, self).__init__()
#         self.dual = None

#         a = {'scale': 1}

#         va = {'x_fix': False,
#               'y_fix': False,
#               'z_fix': False,
#               'is_fixed': False}

#         ea = {'l_min': 1,
#               'l_max': 20,
#               'target_vector': None,
#               'target_length': None}

#         fa = {'a_max': 1000,
#               'target_area': None,
#               'target_normal': None}

#         ca = {}

#         self.attributes.update(a)
#         self.default_vertex_attributes.update(va)
#         self.default_edge_attributes.update(ea)
#         self.default_face_attributes.update(fa)
#         self.default_cell_attributes.update(ca)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   polyhedral force diagram
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


class ForceVolMesh(VolMesh3gs):
    """A polyhedral force diagram, represented as a volmesh object.

    """

    __module__ = 'compas_3gs.diagrams'

    def __init__(self):
        super(ForceVolMesh, self).__init__()
        self.primal = None

        a = {'scale': 1}

        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False,
              'is_fixed': False}

        ea = {'l_min': 1,
              'l_max': 20,
              'target_vector': None,
              'target_length': None}

        fa = {'target_area': None,
              'target_normal': None,
              '_a': 0.0}

        ca = {'dir': None}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)
        self.default_face_attributes.update(fa)
        self.default_cell_attributes.update(ca)


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
