from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import pairwise

from compas.datastructures import VolMesh

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import centroid_points

from compas.geometry import centroid_polygon

from compas_rhino.helpers.volmesh import volmesh_draw
from compas_rhino.artists import VolMeshArtist

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented
from compas_3gs.utilities import datastructure_centroid



__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['VolMesh3gs']


class VolMesh3gs(VolMesh):
    """Inherits and extends the compas VolMesh class, such that it is more suitable for 3D graphic statics applications.

    Primarily used for polyhedral form and force diagrams.

    """

    def __init__(self):
        super(VolMesh3gs, self).__init__()

    # --------------------------------------------------------------------------
    #   inherited functions
    # --------------------------------------------------------------------------

    # cell_split_vertex      = cell_split_vertex
    # datastructure_centroid = datastructure_centroid

    # --------------------------------------------------------------------------
    # misc
    # --------------------------------------------------------------------------

    # def bounding_box(self):

    #     xyz = [self.vertex_coordinates(vkey) for vkey in self.vertex]

    #     x_sorted = sorted(xyz, key=lambda k: k[0])
    #     y_sorted = sorted(xyz, key=lambda k: k[1])
    #     z_sorted = sorted(xyz, key=lambda k: k[2])

    #     x = abs(x_sorted[0][0] - x_sorted[-1][0])
    #     y = abs(y_sorted[0][1] - y_sorted[-1][1])
    #     z = abs(z_sorted[0][2] - z_sorted[-1][2])

    #     return x, y, z

    # --------------------------------------------------------------------------
    #   deleting
    # --------------------------------------------------------------------------

    def cell_vertex_delete(self, vkey):
        '''This removes the vertex, and everything that is attached to the vertex EXCEPT the cell itself.
        '''

        if len(self.cell) > 1:
            raise ValueError('This is a multi-cell volmesh.')
        nbr_vkeys = self.vertex_neighbours(vkey)
        nbr_ckeys = self.vertex_cells(vkey)

        # delete cell info -----------------------------------------------------
        for ckey in nbr_ckeys:
            del self.cell[ckey][vkey]
            for nbr_vkey in nbr_vkeys:
                del self.cell[ckey][nbr_vkey][vkey]

        # delete halffaces -----------------------------------------------------
        halffaces = self.vertex_halffaces(vkey)
        for hfkey in halffaces:
            del self.halfface[hfkey]

        # delete planes --------------------------------------------------------
        del self.plane[vkey]
        for u in self.plane:
            for v in self.plane[u].keys():
                if v == vkey:
                    del self.plane[u][v]
                else:
                    for w in self.plane[u][v].keys():
                        if w == vkey:
                            del self.plane[u][v][w]

        # delete edges ---------------------------------------------------------
        del self.edge[vkey]
        for u in self.edge:
            if vkey in self.edge[u]:
                del self.edge[u][vkey]

        # delete the vertex itself ---------------------------------------------
        del self.vertex[vkey]

    def delete_halfface(self, hfkey):
        vertices = self.halfface_vertices(hfkey)
        for i in range(-2, len(vertices) - 2):
            u = vertices[i]
            v = vertices[i + 1]
            w = vertices[i + 2]
            print(u, v, w)
            del self.plane[u][v][w]
            if self.plane[w][v][u] is None:
                del self.plane[w][v][u]
        del self.halfface[hfkey]

    def delete_cell(self, ckey):

        hfkeys = self.cell_halffaces(ckey)

        for hfkey in hfkeys:
            for halfedge in self.halfface_halfedges(hfkey):
                u, v = halfedge
                # delete edges
                if v in self.edge[u]:
                    if len(self.edge_cells(u, v)) == 1:
                        del self.edge[u][v]
                if u in self.edge[v]:
                    if len(self.edge_cells(v, u)) == 1:
                        del self.edge[v][u]

        # delete vertices
        for vkey in self.cell_vertices(ckey):
            if len(self.vertex_cells(vkey)) == 1:
                del self.vertex[vkey]

        # delete halfface and planes
        for hfkey in hfkeys:
            vertices = self.halfface_vertices(hfkey)
            for i in range(-2, len(vertices) - 2):
                u = vertices[i]
                v = vertices[i + 1]
                w = vertices[i + 2]
                # delete planes
                self.plane[u][v][w] = None
                if self.plane[w][v][u] is None:
                    del self.plane[u][v][w]
                    del self.plane[w][v][u]
            del self.halfface[hfkey]

        # delete cell
        del self.cell[ckey]

    # --------------------------------------------------------------------------
    #   updaters / setters
    # --------------------------------------------------------------------------

    # def update_v_data(self, vkey, attr_dict=None, **kwattr):
    #     if vkey not in self.v_data:
    #         self.v_data[vkey] = {}
    #     attr = self.default_v_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.v_data[vkey].update(attr)

    # def update_e_data(self, u, v, attr_dict=None, **kwattr):
    #     if (u, v) not in self.e_data:
    #         self.e_data[u, v] = {}
    #     attr = self.default_e_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.e_data[u, v].update(attr)

    # def update_f_data(self, fkey, attr_dict=None, **kwattr):
    #     if fkey not in self.f_data:
    #         self.f_data[fkey] = {}
    #     attr = self.default_f_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.f_data[fkey].update(attr)

    # def update_c_data(self, ckey, attr_dict=None, **kwattr):
    #     if ckey not in self.c_data:
    #         self.c_data[ckey] = {}
    #     attr = self.default_c_prop.copy()
    #     if not attr_dict:
    #         attr_dict = {}
    #     attr_dict.update(kwattr)
    #     attr.update(attr_dict)
    #     self.c_data[ckey].update(attr)

    # def initialize_data(self):
    #     for vkey in self.vertex:
    #         self.update_v_data(vkey)
    #     for u, v in self.edges():
    #         self.update_e_data(u, v)
    #     for fkey in self.halfface:
    #         self.update_f_data(fkey)
    #     for ckey in self.cell:
    #         self.update_c_data(ckey)

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

    # --------------------------------------------------------------------------
    #   vertices
    # --------------------------------------------------------------------------

    # def vertex_halffaces(self, vkey):
    #     # halffaces = []
    #     # for ckey in self.vertex_cells(vkey):
    #     #     print(vkey, self.cell[ckey])
    #     #     halffaces += self.cell[ckey][vkey].values()
    #     # return halffaces

    #     cells = self.vertex_cells(vkey)

    #     nbr_vkeys = self.plane[vkey].keys()

    #     halffaces = []
    #     for ckey in cells:
    #         for v in nbr_vkeys:
    #             if v in self.cell[ckey][vkey]:
    #                 halffaces.append(self.cell[ckey][vkey][v])
    #                 halffaces.append(self.cell[ckey][v][vkey])
    #     return halffaces

    # def vertex_normal(self, vkey):
    #     vectors = []
    #     for hfkey in self.vertex_halffaces(vkey):
    #         if self.is_halfface_on_boundary(hfkey):
    #             vectors.append(self.halfface_oriented_normal(hfkey))
    #     return normalize_vector(centroid_points(vectors))

    # def vertex_cells(self, vkey):
    #     ckeys = set()
    #     for v in self.plane[vkey].keys():
    #         for w in self.plane[vkey][v].keys():
    #             if self.plane[vkey][v][w] is not None:
    #                 ckeys.add(self.plane[vkey][v][w])
    #     return list(ckeys)

    def vertex_update_xyz(self, vkey, xyz, constrained=True):
        if constrained:
            # X
            if self.vertex[vkey]['x_fix'] is False:
                self.vertex[vkey]['x'] = xyz[0]
            # Y
            if self.vertex[vkey]['y_fix'] is False:
                self.vertex[vkey]['y'] = xyz[1]
            # Z
            if self.vertex[vkey]['z_fix'] is False:
                self.vertex[vkey]['z'] = xyz[2]
        else:
            self.vertex[vkey]['x'] = xyz[0]
            self.vertex[vkey]['y'] = xyz[1]
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

    # def edge_halffaces(self, u, v):
    #     """All halffaces of a volmesh that has edge u-v.
    #     """
    #     hfkeys = []
    #     for hfkey in self.halfface:
    #         if all(vkey in self.halfface[hfkey] for vkey in (u, v)):
    #             hfkeys.append(hfkey)
    #     return hfkeys

    # def edge_cells(self, u, v, ordered=False):

    #     ckeys = set()
    #     for hfkey in self.edge_halffaces(u, v):
    #         u, v, w = self.halfface[hfkey][0:3]
    #         ckey = self.halfface_cell(hfkey)
    #         ckeys.add(ckey)

    #     return list(ckeys)

    # --------------------------------------------------------------------------
    # halffaces and faces
    # --------------------------------------------------------------------------

    # def face_center(self, fkey):
    #     return centroid_polygon(self.halfface_coordinates(fkey))

    # def halfface_coordinates(self, hfkey):
    #     return [self.vertex_coordinates(key) for key in self.halfface_vertices(hfkey)]

    # def halfface_center(self, hfkey):
    #     return centroid_polygon(self.halfface_coordinates(hfkey))

    # def halfface_halfedges(self, hfkey):
    #     vertices = self.halfface_vertices(hfkey)
    #     return list(pairwise(vertices + vertices[0:1]))

    def halfface_oriented_area(self, hfkey):
        vertices = self.halfface_vertices(hfkey)
        points   = [self.vertex_coordinates(vkey) for vkey in vertices]
        area     = polygon_area_oriented(points)
        return area

    def halfface_oriented_normal(self, hfkey, unitized=True):
        vertices = self.halfface_vertices(hfkey)
        points   = [self.vertex_coordinates(vkey) for vkey in vertices]
        normal   = polygon_normal_oriented(points, unitized)
        if length_vector(normal) == 0 :
            uv = subtract_vectors(points[1], points[0])
            vw = subtract_vectors(points[2], points[1])
            normal = normalize_vector(cross_vectors(uv, vw))
        return normal

    # def halfface_vertex_ancestor(self, hfkey, key):
    #     i = self.halfface[hfkey].index(key)
    #     return self.halfface[hfkey][i - 1]

    # def halfface_vertex_descendent(self, hfkey, key):
    #     if self.halfface[hfkey][-1] == key:
    #         return self.halfface[hfkey][0]
    #     i = self.halfface[hfkey].index(key)
    #     return self.halfface[hfkey][i + 1]

    # def halfface_opposite_halfface(self, hfkey):
    #     u = self.halfface[hfkey][0]
    #     v = self.halfface[hfkey][1]
    #     w = self.halfface[hfkey][2]
    #     nbr_ckey = self.plane[w][v][u]
    #     if not nbr_ckey:
    #         return None
    #     return self.cell[nbr_ckey][v][u]

    # def halffaces_on_boundary(self):
    #     halffaces = []
    #     for ckey in self.cell:
    #         hfkeys = self.cell_halffaces(ckey)
    #         for hfkey in hfkeys:
    #             u = self.halfface[hfkey][0]
    #             v = self.halfface[hfkey][1]
    #             w = self.halfface[hfkey][2]
    #             if self.plane[w][v][u] is None:
    #                 halffaces.append(hfkey)
    #     return halffaces

    # def halffaces_interior(self):
    #     halffaces = set(self.halfface.keys())
    #     hf_boundary = set(self.halffaces_on_boundary())
    #     return halffaces - hf_boundary

    def halfface_dependent_halffaces(self, hfkey):
        dep_hfkeys = {}
        ckey       = self.halfface_cell(hfkey)
        hf_edges   = self.halfface_halfedges(hfkey)
        for edge in hf_edges:
            u = edge[0]
            v = edge[1]
            adj_hfkey = self.cell[ckey][v][u]
            w         = self.halfface_vertex_ancestor(adj_hfkey, v)
            nbr_ckey  = self.plane[u][v][w]
            if nbr_ckey is not None:
                dep_hfkey = self.cell[nbr_ckey][v][u]
                dep_hfkeys[dep_hfkey] = u
        return dep_hfkeys

    def volmesh_all_dependent_halffaces(self, hfkey):
        dependents = set(self.halfface_dependent_halffaces(hfkey).keys())
        seen = set()
        i = 0
        while True:
            if i == 100:
                break
            if i != 0 and len(seen) == 0:
                break
            temp = []
            for dep_hfkey in dependents:
                if dep_hfkey not in seen:
                    hfkeys = self.halfface_dependent_halffaces(dep_hfkey).keys()
                    temp += hfkeys
                    seen.add(dep_hfkey)
            dependents.update(temp)
            i += 1
        if hfkey in dependents:
            dependents.remove(hfkey)
        return list(dependents)

    # --------------------------------------------------------------------------
    #   cells
    # --------------------------------------------------------------------------

    # def cell_halffaces(self, ckey):
    #     halffaces = set()
    #     for u in self.cell[ckey]:
    #         for v in self.cell[ckey][u]:
    #             fkey = self.cell[ckey][u][v]
    #             halffaces.add(fkey)
    #     return list(halffaces)

    # def cell_vertex_neighbours(self, ckey, vkey):
    #     nbr_vkeys = self.cell[ckey][vkey].keys()
    #     u = vkey
    #     v = nbr_vkeys[0]
    #     ordered_vkeys = [v]
    #     for i in range(len(nbr_vkeys) - 1):
    #         hfkey = self.cell[ckey][u][v]
    #         v     = self.halfface_vertex_ancestor(hfkey, u)
    #         ordered_vkeys.append(v)
    #     return ordered_vkeys

    # def cell_vertex_halffaces(self, ckey, vkey):
    #     nbr_vkeys = self.cell[ckey][vkey].keys()
    #     u = vkey
    #     v = nbr_vkeys[0]
    #     ordered_hfkeys = []
    #     for i in range(len(nbr_vkeys)):
    #         hfkey = self.cell[ckey][u][v]
    #         v     = self.halfface_vertex_ancestor(hfkey, u)
    #         ordered_hfkeys.append(hfkey)
    #     return ordered_hfkeys

    # def cell_halfface_neighbours(self, ckey, hfkey):
    #     """Includes both edge and vertex neighbours.

    #     note to self: why... would this be useful?
    #     """
    #     hf_vkeys = self.halfface[hfkey]
    #     hf_nbrs = []
    #     for vkey in hf_vkeys:
    #         nbrs = self.cell_vertex_halffaces(ckey, vkey)
    #         for key in nbrs:
    #             if key not in hf_nbrs and key != hfkey:
    #                 hf_nbrs.append(key)
    #     return hf_nbrs

    # def cell_pair_halffaces(self, ckey_1, ckey_2):
    #     """Given 2 ckeys, returns the interfacing halffaces, respectively.
    #     """
    #     for hfkey in self.cell_halffaces(ckey_1):
    #         u   = self.halfface[hfkey][0]
    #         v   = self.halfface[hfkey][1]
    #         w   = self.halfface[hfkey][2]
    #         nbr = self.plane[w][v][u]
    #         if nbr == ckey_2:
    #             return hfkey, self.halfface_opposite_halfface(hfkey)
    #     return

    # --------------------------------------------------------------------------
    # queries
    # --------------------------------------------------------------------------

    # def is_vertex_on_boundary(self, vkey):
    #     hfkeys = self.vertex_halffaces(vkey)
    #     for hfkey in hfkeys:
    #         if self.is_halfface_on_boundary(hfkey):
    #             return True
    #     return False

    # def is_halfface_on_boundary(self, hfkey):
    #     u   = self.halfface[hfkey][0]
    #     v   = self.halfface[hfkey][1]
    #     w   = self.halfface[hfkey][2]
    #     if self.plane[w][v][u] is None:
    #         return True
    #     return False

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
        artist = VolMeshArtist(self)
        # artist.clear()
        volmesh_draw(self, layer=self.layer)

    def clear(self):
        artist = VolMeshArtist(self)
        # self.clear_cell_labels()
        artist.clear()

    def draw_edges(self, **kwattr):
        artist = VolMeshArtist(self, **kwattr)
        artist.draw_edges(**kwattr)

    def clear_edges(self, **kwattr):
        artist = VolMeshArtist(self, **kwattr)
        artist.clear_edges(**kwattr)

    def draw_faces(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.draw_faces(**kwattr)

    def clear_faces(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.clear_faces(**kwattr)

    def draw_face_labels(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.draw_facelabels(**kwattr)

    def draw_vertices(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.draw_vertices(**kwattr)

    def draw_vertex_labels(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.draw_vertexlabels(**kwattr)

    def draw_edge_labels(self, **kwattr):
        artist = VolMeshArtist(self)
        artist.draw_edgelabels(**kwattr)

    # def draw_face_normals(self, **kwattr):
    #     draw_volmesh_face_normals(self, **kwattr)

    # def draw_cell(self, ckeys):
    #     draw_cell(self, ckeys)

    # def draw_cell_labels(self, **kwattr):
    #     draw_cell_labels(self, **kwattr)

    # def clear_cell_labels(self):
    #     clear_cell_labels(self)

    # def draw_egi_arcs(self, draw_arcs=False, **kwattr):
    #     for ckey in self.cell:
    #         egi = self.c_data[ckey]['egi']
    #         draw_egi_arcs(egi)
    #         egi.draw_edges()
    #         egi.draw_facelabels(color=(150, 150, 150))
    #         egi.draw_vertexlabels(color=(255, 150, 150))


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

