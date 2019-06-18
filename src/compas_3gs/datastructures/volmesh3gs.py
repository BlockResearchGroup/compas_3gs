from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import VolMesh

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import cross_vectors

from compas_rhino.helpers.volmesh import volmesh_draw
from compas_rhino.artists import VolMeshArtist

from compas_3gs.utilities import polygon_normal_oriented
from compas_3gs.utilities import polygon_area_oriented


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
    #   vertices
    # --------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------
    # halffaces and faces
    # --------------------------------------------------------------------------

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

    def clean(self):
        pass

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    def draw(self, **kwattr):
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
