from __future__ import print_function

from compas.datastructures import VolMesh

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector

from compas.geometry import area_polygon
from compas.geometry import normal_polygon
from compas.geometry import center_of_mass_polygon

from compas_rhino.helpers.volmesh import volmesh_draw
from compas_rhino.helpers.artists.volmeshartist import VolMeshArtist

from compas_3gs.rhino.display import draw_celllabels


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


class VolMesh3gs(VolMesh):
    """Inherits and extends the VolMesh class, such that it is more suitable for 3DGS purposes.

    Primarily used for polyhedral form and force diagrams.

    """

    def __init__(self):
        super(VolMesh3gs, self).__init__()

        self.v_data = {}
        self.e_data = {}
        self.f_data = {}
        self.c_data = {}

        self.default_v_prop = {}
        self.default_e_prop = {}
        self.default_f_prop = {}
        self.default_c_prop = {}

    # --------------------------------------------------------------------------
    #   updaters / setters
    # --------------------------------------------------------------------------

    def update_v_data(self, vkey, attr_dict=None, **kwattr):
        if vkey not in self.v_data:
            self.v_data[vkey] = {}
        attr = self.default_v_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.v_data[vkey].update(attr)

    def update_e_data(self, u, v, attr_dict=None, **kwattr):
        if (u, v) not in self.e_data:
            self.e_data[u, v] = {}
        attr = self.default_e_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.e_data[u, v].update(attr)

    def update_f_data(self, fkey, attr_dict=None, **kwattr):
        if fkey not in self.f_data:
            self.f_data[fkey] = {}
        attr = self.default_f_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.f_data[fkey].update(attr)

    def update_c_data(self, ckey, attr_dict=None, **kwattr):
        if ckey not in self.c_data:
            self.c_data[ckey] = {}
        attr = self.default_c_prop.copy()
        if not attr_dict:
            attr_dict = {}
        attr_dict.update(kwattr)
        attr.update(attr_dict)
        self.c_data[ckey].update(attr)

    def initialize_data(self):
        for vkey in self.vertex:
            self.update_v_data(vkey)
        for u, v in self.edges():
            self.update_e_data(u, v)
        for fkey in self.halfface:
            self.update_f_data(fkey)
        for ckey in self.cell:
            self.update_c_data(ckey)

    # def update_data(self):
    #     for vkey in self.vertex:
    #         if vkey not in self.v_data:
    #             self.v_data[vkey] = self.default_v_prop.copy()
    #     for u, v in self.edges():
    #         if u not in self.e_data:
    #             self.e_data[u, v] = self.default_e_prop.copy()
    #     for fkey in self.halfface:
    #         if fkey not in self.f_data:
    #             self.f_data[fkey] = self.default_f_prop.copy()
    #     for ckey in self.cell:
    #         if ckey not in self.c_data:
    #             self.c_data[ckey] = self.default_c_prop.copy()

    # --------------------------------------------------------------------------
    #   iterators
    # --------------------------------------------------------------------------

    def halfface_iter(self, data=False):
        for hfkey in self.halfface:
            if data:
                yield hfkey, self.halfface[hfkey]
            else:
                yield hfkey

    def edges_iter(self, data=False):
        for u in self.edge:
            for v in self.edge[u]:
                if data:
                    yield u, v, self.edge[u][v]
                else:
                    yield u, v

    # --------------------------------------------------------------------------
    #   vertices
    # --------------------------------------------------------------------------

    def vertex_halffaces(self, vkey):
        halffaces = []
        for hfkey in self.halfface:
            if vkey in self.halfface[hfkey]:
                halffaces.append(hfkey)
        return halffaces

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
    #   edges
    # --------------------------------------------------------------------------

    def edge_vector(self, u, v, unitized=True):
        u_xyz  = self.vertex_coordinates(u)
        v_xyz  = self.vertex_coordinates(v)
        vector = subtract_vectors(v_xyz, u_xyz)
        if unitized:
            return normalize_vector(vector)
        return vector

    def edge_halffaces(self, u, v):
        hfkeys = []
        for hfkey in self.halfface:
            if all(vkey in self.halfface[hfkey] for vkey in (u, v)):
                hfkeys.append(hfkey)
        return hfkeys

    def edge_cells(self, u, v, ordered=False):
        ckeys = set(self.halfface_cell(key) for key in self.edge_halffaces(u, v))
        return list(ckeys)

    # --------------------------------------------------------------------------
    # halffaces and faces
    # --------------------------------------------------------------------------

    def face_center(self, fkey):
        return center_of_mass_polygon(self.halfface_coordinates(fkey))

    def halfface_coordinates(self, hfkey):
        return [self.vertex_coordinates(key) for key in self.halfface_vertices(hfkey)]

    def halfface_center(self, hfkey):
        return center_of_mass_polygon(self.halfface_coordinates(hfkey))

    def halfface_area(self, hfkey):
        hf_vkeys = self.halfface_vertices(hfkey)
        hf_v_xyz = [self.vertex_coordinates(vkey) for vkey in hf_vkeys]
        area     = area_polygon(hf_v_xyz)
        return area

    def halfface_normal(self, hfkey):
        vertices = self.halfface_vertices(hfkey)
        normal   = normal_polygon([self.vertex_coordinates(vkey) for vkey in vertices])
        return normal

    def halfface_vertex_ancestor(self, hfkey, key):
        i = self.halfface[hfkey].index(key)
        return self.halfface[hfkey][i - 1]

    def halfface_vertex_descendant(self, hfkey, key):
        if self.halfface[hfkey][-1] == key:
            return self.halfface[hfkey][0]
        i = self.halfface[hfkey].index(key)
        return self.halfface[hfkey][i + 1]

    def halfface_pair(self, hfkey):
        u   = self.halfface[hfkey][0]
        v   = self.halfface[hfkey][1]
        w   = self.halfface[hfkey][2]
        nbr_ckey = self.plane[w][v][u]
        if not nbr_ckey:
            return None
        return self.cell[nbr_ckey][v][u]

    def halffaces_on_boundary(self):
        halffaces = []
        for ckey in self.cell:
            hfkeys = self.cell_halffaces(ckey)
            for hfkey in hfkeys:
                u   = self.halfface[hfkey][0]
                v   = self.halfface[hfkey][1]
                w   = self.halfface[hfkey][2]
                if self.plane[w][v][u] is None:
                    halffaces.append(hfkey)
        return halffaces

    # --------------------------------------------------------------------------
    #   cells
    # --------------------------------------------------------------------------

    def cell_vertex_neighbours(self, ckey, vkey, ordered=True):
        cell_vertices = self.cell_vertices(ckey)
        nbr_vkeys = []
        for nbr_vkey in self.vertex_neighbours(vkey):
            if nbr_vkey in cell_vertices:
                nbr_vkeys.append(nbr_vkey)
        if not ordered:
            return nbr_vkeys
        u       = vkey
        v       = nbr_vkeys[0]
        ordered = [v]
        for i in range(len(nbr_vkeys) - 1):
            hfkey = self.cell[ckey][u][v]
            v     = self.halfface_vertex_ancestor(hfkey, u)
            ordered.append(v)
        return ordered

    def cell_vertex_halffaces(self, ckey, vkey):
        nbr_vkeys = self.cell[ckey][vkey].keys()
        u       = vkey
        v       = nbr_vkeys[0]
        ordered = []
        for i in range(len(nbr_vkeys) - 1):
            hfkey = self.cell[ckey][u][v]
            v     = self.halfface_vertex_ancestor(hfkey, u)
            ordered.append(hfkey)
        return ordered

    def cell_pair_hfkeys(self, ckey_1, ckey_2):
        for hfkey in self.cell_halffaces(ckey_1):
            u   = self.halfface[hfkey].iterkeys().next()
            v   = self.halfface[hfkey][u]
            w   = self.halfface[hfkey][v]
            nbr = self.plane[w][v][u]
            if nbr == ckey_2:
                return hfkey, self.halfface_pair(hfkey)
        return

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        volmesh_draw(self, **kwattr)

    def draw_vertexlabels(self):
        artist = VolMeshArtist(self)
        artist.draw_vertexlabels()

    def draw_facelabels(self):
        artist = VolMeshArtist(self)
        artist.draw_facelabels()

    def draw_edgelabels(self):
        artist = VolMeshArtist(self)
        artist.draw_edgelabels()

    def draw_celllabels(self):
        draw_celllabels(self)
