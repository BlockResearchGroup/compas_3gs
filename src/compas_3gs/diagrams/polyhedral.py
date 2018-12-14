from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_3gs.datastructures import Network3gs
from compas_3gs.datastructures import VolMesh3gs


__author__    = ['Juney Lee']
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['FormNetwork',
           'FormVolMesh',

           'ForceVolMesh']


# ==============================================================================
#   polyheral form diagram - as network
# ==============================================================================


class FormNetwork(Network3gs):
    """A polyhedral form diagram, represented as a network object.

    """

    def __init__(self):
        super(FormNetwork, self).__init__()

        a  = {'scale': 1}

        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False}

        ea = {'l_min': 1,
              'l_max': 20,
              'target_vector': None,
              'target_length': None}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)


# ==============================================================================
#   polyheral form diagram - as volmesh
# ==============================================================================


class FormVolMesh(VolMesh3gs):
    """A polyhedral form diagram, represented as a volmesh object.

    """

    def __init__(self):
        super(FormVolMesh, self).__init__()

        a  = {'scale': 1}

        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False}

        ea = {'l_min': 1,
              'l_max': 20,
              'target_vector': None,
              'target_length': None}

        fa = {'a_max': 1000,
              'target_area'  : None,
              'target_normal': None}

        ca = {}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)
        self.default_face_attributes.update(fa)
        self.default_cell_attributes.update(ca)


# ==============================================================================
#   polyhedral force diagram
# ==============================================================================


class ForceVolMesh(VolMesh3gs):
    """A polyhedral force diagram, represented as a volmesh object.

    """

    def __init__(self):
        super(ForceVolMesh, self).__init__()

        a  = {'scale': 1}

        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False}

        ea = {'l_min': 1,
              'l_max': 20,
              'target_vector': None,
              'target_length': None}

        fa = {'target_area'  : None,
              'target_normal': None}

        ca = {'dir': None}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)
        self.default_face_attributes.update(fa)
        self.default_cell_attributes.update(ca)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':

    pass
