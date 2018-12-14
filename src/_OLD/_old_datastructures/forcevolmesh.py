from __future__ import print_function

from compas_3gs.datastructures.volmesh3gs import VolMesh3gs as VolMesh


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


class ForceVolMesh(VolMesh):
    """Class representing a 3D force diagram as a VolMesh object.
    """

    def __init__(self):
        super(ForceVolMesh, self).__init__()
        # set global attributes ------------------------------------------------
        self.v_data = {}
        self.e_data = {}
        self.f_data = {}
        self.c_data = {}
        self.colors = {
            'vertex'  : {'default' : (0, 0, 0),
                         'fixed'   : (255, 0, 0)},
            'edge'    : {'default' : (0, 0, 0)},
            'halfface': {},
            'cell'    : {}}
        # default properties ---------------------------------------------------
        self.default_v_prop = {
            'x_fix': False,
            'y_fix': False,
            'z_fix': False
        }
        self.default_e_prop = {
            'e_fix'        : False,
            'target_length': None
        }
        self.default_f_prop = {
            'fix_area'  : False,
            'fix_normal': False,
            'is_leaf'   : False
        }
        self.default_c_prop = {
            'egi'       : None
        }
