from __future__ import print_function

from compas_3gs.datastructures._3gs_volmesh import _3gs_VolMesh as VolMesh


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
#
#   3D force diagram as VolMesh
#
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================

class ForceVM(VolMesh):
    """Class representing a 3D force diagram as a VolMesh object.
    """

    def __init__(self):
        super(ForceVM, self).__init__()
        # set global attributes ------------------------------------------------
        self.attributes.update({'name': 'force_vm'})
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
            'e_fix'        : False,
            'target_length': None}
        self.default_f_prop = {
            'fix_area'  : False,
            'fix_normal': False,
            'is_leaf'   : False}
        self.default_c_prop = {}

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

    # # --------------------------------------------------------------------------
    # # iterators
    # # --------------------------------------------------------------------------
    # def halfface_iter(self, data=False):
    #     for hfkey in self.halfface:
    #         if data:
    #             yield hfkey, self.halfface[hfkey]
    #         else:
    #             yield hfkey

    # def edges_iter(self, data=False):
    #     for u in self.edge:
    #         for v in self.edge[u]:
    #             if data:
    #                 yield u, v, self.edge[u][v]
    #             else:
    #                 yield u, v

    # # --------------------------------------------------------------------------
    # # boundary
    # # --------------------------------------------------------------------------
    # def halffaces_on_boundary(self):
    #     halffaces = []
    #     for ckey in self.cell:
    #         hfkeys = self.cell_halffaces(ckey)
    #         for hfkey in hfkeys:
    #             nbr_cells = self.halfface_cell(hfkey)
    #             if nbr_cells is None:
    #                 halffaces.append(hfkey)
    #     return halffaces


    # # --------------------------------------------------------------------------
    # # helpers - edges
    # # --------------------------------------------------------------------------

    # def vertex_halffaces(self, vkey):
    #     halffaces = []
    #     for hfkey in self.halfface:
    #         if vkey in self.halfface[hfkey]:
    #             halffaces.append(hfkey)
    #     return halffaces

    # # --------------------------------------------------------------------------
    # # helpers - edges
    # # --------------------------------------------------------------------------

    # def edge_cells(self, u, v, ordered=False):
    #     pass

    # # --------------------------------------------------------------------------
    # # helpers - halffaces
    # # --------------------------------------------------------------------------

    # def halfface_center(self, hfkey):
    #     vertices = self.halfface_vertices(hfkey, ordered=True)
    #     center   = centroid_points([self.vertex_coordinates(vkey) for vkey in vertices])
    #     return center

    # def halfface_area(self, hfkey):
    #     hf_vkeys = self.halfface_vertices(hfkey, ordered=True)
    #     hf_v_xyz = [self.vertex_coordinates(vkey) for vkey in hf_vkeys]
    #     area     = area_polygon(hf_v_xyz)
    #     return area

    # def halfface_normal(self, hfkey):
    #     vertices = self.halfface_vertices(hfkey, ordered=True)
    #     normal   = normal_polygon([self.vertex_coordinates(vkey) for vkey in vertices])
    #     return normal

    # def halfface_pair(self, hfkey):
    #     u   = self.halfface[hfkey].iterkeys().next()
    #     v   = self.halfface[hfkey][u]
    #     w   = self.halfface[hfkey][v]
    #     for nbr_hfkey in self.halfface:
    #         if all(vkey in self.halfface[nbr_hfkey] for vkey in (u, v, w)):
    #             if nbr_hfkey is not hfkey:
    #                 return nbr_hfkey
    #     return None

    # # --------------------------------------------------------------------------
    # # helpers - cell
    # # --------------------------------------------------------------------------

    # def cell_direction(self, key):
    #     pass


    # # --------------------------------------------------------------------------
    # # drawing
    # # --------------------------------------------------------------------------

    # def draw(self, **kwattr):
    #     volmesh_draw(self, **kwattr)
