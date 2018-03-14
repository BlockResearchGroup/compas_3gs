from compas_3gs.datastructures._3gs_volmesh import _3gs_VolMesh as VolMesh
from compas.datastructures.network import Network

from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors
from compas.geometry import length_vector

from compas_rhino.helpers.volmesh import volmesh_draw
from compas_rhino.helpers.network import network_draw


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   3D form diagram as Network
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

class FormNW(Network):
    """Class representing a 3D form diagram as a Network object.
    """

    def __init__(self):
        super(FormNW, self).__init__()

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

    # --------------------------------------------------------------------------
    # iterators
    # --------------------------------------------------------------------------

    def edges_iter(self, data=False):
        for u in self.edge:
            for v in self.edge[u]:
                if data:
                    yield u, v, self.edge[u][v]
                else:
                    yield u, v

    # --------------------------------------------------------------------------
    # setters
    # --------------------------------------------------------------------------

    def update_data(self):
        for vkey in self.vertex:
            if vkey not in self.v_data:
                self.v_data[vkey] = self.default_v_prop.copy()
        for u, v in self.edges():
            if u not in self.e_data:
                self.e_data[u] = {v: self.default_e_prop.copy()}

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_update_xyz(self, vkey, xyz):
        # X
        if self.v_data[vkey]['x_fix'] is False:
            self.vertex[vkey]['x'] = xyz[0]
        # Y
        if self.v_data[vkey]['y_fix'] is False:
            self.vertex[vkey]['y'] = xyz[1]
        # Z
        if self.v_data[vkey]['z_fix'] is False:
            self.vertex[vkey]['z'] = xyz[2]

    # --------------------------------------------------------------------------
    # helpers - edges
    # --------------------------------------------------------------------------

    def edge_vector(self, u, v, unitized=True):
        u_xyz  = self.vertex_coordinates(u)
        v_xyz  = self.vertex_coordinates(v)
        vector = subtract_vectors(v_xyz, u_xyz)
        if unitized:
            return normalize_vector(vector)
        return vector

    def edge_avg_length(self):
        sum_length = 0
        edge_count = 0
        for u, v in self.edges_iter():
            edge_vector = self.edge_vector(u, v, unitized=False)
            sum_length += length_vector(edge_vector)
            edge_count += 1
        return sum_length / edge_count

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        network_draw(self, **kwattr)


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   3D form diagram as VolMesh
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************

class FormVM(VolMesh):
    """Class representing a 3D form diagram as a VolMesh object.
    """

    def __init__(self):
        super(FormVM, self).__init__()
        # set global attributes ------------------------------------------------
        self.attributes.update({'name': 'form_vm'})
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
            'z_fix': False}
        self.default_e_prop = {
            'e_fix': False,
            'test' : None}
        self.default_f_prop = {
            'fix_area'  : False,
            'fix_normal': False,
            'is_leaf'   : False}
        self.default_c_prop = {
            'test': None}

    # --------------------------------------------------------------------------
    # setters
    # --------------------------------------------------------------------------

    def update_data(self):
        for vkey in self.vertex:
            if vkey not in self.v_data:
                self.v_data[vkey] = self.default_v_prop.copy()
        for u, v in self.edges_iter():
            if u not in self.e_data:
                self.e_data[u] = {v: self.default_e_prop.copy()}
        for fkey in self.halfface:
            if fkey not in self.f_data:
                self.f_data[fkey] = self.default_f_prop.copy()
        for ckey in self.cells():
            if ckey not in self.c_data:
                self.c_data[ckey] = self.default_c_prop.copy()

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        volmesh_draw(self, **kwattr)
