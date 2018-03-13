from __future__ import print_function

from compas.datastructures.volmesh import VolMesh

from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import angle_vectors
from compas.geometry import normalize_vector

from compas.geometry import translate_points
from compas.geometry import rotate_points

from compas.geometry import area_polygon
from compas.geometry import normal_polygon
from compas.geometry import centroid_points



from compas_rhino.helpers.volmesh import volmesh_draw

from compas_3gs.helpers import sort_points_ccw

__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


class _3gs_VolMesh(VolMesh):
    """Extension of the VolMesh class, adding built in more functions.

    These functions should eventually be added to the compas-dev VolMesh class...

    """

    def __init__(self):
        super(_3gs_VolMesh, self).__init__()

    # --------------------------------------------------------------------------
    # iterators
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
    # boundary
    # --------------------------------------------------------------------------

    def halffaces_on_boundary(self):
        halffaces = []
        for ckey in self.cell:
            hfkeys = self.cell_halffaces(ckey)
            for hfkey in hfkeys:
                nbr_hfkey = self.halfface_pair(hfkey)
                if nbr_hfkey is None:
                    halffaces.append(hfkey)
        return halffaces

    # --------------------------------------------------------------------------
    # helpers - vertices
    # --------------------------------------------------------------------------

    def vertex_halffaces(self, vkey):
        halffaces = []
        for hfkey in self.halfface:
            if vkey in self.halfface[hfkey]:
                halffaces.append(hfkey)
        return halffaces

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

    def edge_halffaces(self, u, v):
        hfkeys = []
        for hfkey in self.halfface:
            if all(vkey in self.halfface[hfkey] for vkey in (u, v)):
                hfkeys.append(hfkey)
        return hfkeys

    def edge_cells(self, u, v, ordered=False):
        """Ordering based on the right hand rule, along the edge.
        If u-v is the normal, then the cells are ordered in ccw.
        """
        ckeys   = [self.halfface_cell(hfkey) for hfkey in self.edge_halffaces(u, v)]
        c_xyz   = {ckey: self.cell_centroid(ckey) for ckey in ckeys}
        normal  = self.edge_vector(u, v, unitized=True)
        plane   = [self.vertex_coordinates(u), normal]
        ordered = sort_points_ccw(c_xyz, plane)
        return ordered

    # --------------------------------------------------------------------------
    # helpers - halffaces
    # --------------------------------------------------------------------------

    def halfface_center(self, hfkey):
        vertices = self.halfface_vertices(hfkey, ordered=True)
        center   = centroid_points([self.vertex_coordinates(vkey) for vkey in vertices])
        return center

    def halfface_area(self, hfkey):
        hf_vkeys = self.halfface_vertices(hfkey, ordered=True)
        hf_v_xyz = [self.vertex_coordinates(vkey) for vkey in hf_vkeys]
        area     = area_polygon(hf_v_xyz)
        return area

    def halfface_normal(self, hfkey):
        vertices = self.halfface_vertices(hfkey, ordered=True)
        normal   = normal_polygon([self.vertex_coordinates(vkey) for vkey in vertices])
        return normal

    def halfface_pair(self, hfkey):
        u   = self.halfface[hfkey].iterkeys().next()
        v   = self.halfface[hfkey][u]
        w   = self.halfface[hfkey][v]
        for nbr_hfkey in self.halfface:
            if all(vkey in self.halfface[nbr_hfkey] for vkey in (u, v, w)):
                if nbr_hfkey is not hfkey:
                    return nbr_hfkey
        return None

    # --------------------------------------------------------------------------
    # helpers - cell
    # --------------------------------------------------------------------------

    def cell_pair_hfkeys(self, ckey_1, ckey_2):
        cell_pair_hfkeys = {}
        for hfkey in self.cell_halffaces(ckey_1):
            u   = self.halfface[hfkey].iterkeys().next()
            v   = self.halfface[hfkey][u]
            w   = self.halfface[hfkey][v]
            nbr = self.plane[w][v][u]
            if nbr == ckey_2:
                return hfkey, self.halfface_pair(hfkey)
        return

    def cell_direction(self, key):
        """

        Will this be really useful?

        What happens for concave and complex cells?

        """
        center = self.cell_centroid(ckey)
        halfface = self.cell_halffaces(ckey)
        pass

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        volmesh_draw(self, **kwattr)
