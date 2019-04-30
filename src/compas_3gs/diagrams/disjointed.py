from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_3gs.datastructures import Network3gs

from compas_3gs.diagrams import Cell


__all__ = ['CellNetwork']


class CellNetwork(Network3gs):
    """A disjointed, non-polyhedral form and force diagram.

    """

    def __init__(self):
        super(FormNetwork, self).__init__()

        a  = {'gfp'  : Cell()}
        va = {'x_fix': False,
              'y_fix': False,
              'z_fix': False,
              'cell' : Cell()}
        ea = {'target_vector': None,
              'target_length': None}


        # stores all the cells here with vkeys....
        self.cells = {}

        self.attributes.update(a)
        self.default_vertex_attributes.update(va)
        self.default_edge_attributes.update(ea)

