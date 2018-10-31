from compas_3gs.datastructures.network3gs import Network3gs as Network

from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors
from compas.geometry import length_vector

from compas_rhino.helpers.network import network_draw


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


class FormNetwork(Network):
    """Class representing a 3D form diagram as a Network object.
    """

    def __init__(self):
        super(FormNetwork, self).__init__()

        # set global attributes ------------------------------------------------
        self.attributes.update({'name': 'form_nw'})
        self.v_data = {}
        self.e_data = {}
        self.colors = {
            'object': (0, 0, 0),
            'vertex': {'is_fixed'      : (255, 0, 0),
                       'is_boundary'   : (0, 153, 0),
                       'is_free'       : (0, 0, 0)},
            'edge'  : {'boundary'      : (0, 0, 0),
                       'compression'   : (0, 0, 0),
                       'tension'       : (0, 0, 0),
                       'warning'       : (255, 0, 0)},
            'face'  : (0, 0, 0)}

        # default properties ---------------------------------------------------
        self.default_v_prop = {
            'x_fix': False,
            'y_fix': False,
            'z_fix': False}
        self.default_e_prop = {
            'f_target'    : None,
            'l_target'    : None}
