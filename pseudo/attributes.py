class VolMesh():

    def __init__(self):
        super(VolMesh, self).__init__()

        self.vertex      = {}
        self.edge        = {}
        self.halfface    = {}
        self.cell        = {}
        self.plane       = {}

        self.attributes  = {'name'        : 'VolMesh',
                            'color.vertex': (255, 255, 255),
                            'color.edge'  : (0, 0, 0),
                            # ...
                            }

        self.default_v_attributes = {'x'         : 0.0,
                                     'y'         : 0.0,
                                     'z'         : 0.0,
                                     'x_fix'     : False,
                                     'y_fix'     : False,
                                     'z_fix'     : False
                                     # ...
                                     }
        self.default_e_attributes = {'e_fix'     : False,
                                     'target_l'  : None
                                     # ...
                                     }
        self.default_f_attributes = {'target_n'  : None,
                                     'fix_area'  : False,
                                     'fix_normal': False,
                                     'is_leaf'   : False
                                     # ...
                                     }
        self.default_c_attributes = {'egi'       : None
                                     # ...
                                     }

        self.v_data = {}
        self.e_data = {}
        self.f_data = {}
        self.c_data = {}
