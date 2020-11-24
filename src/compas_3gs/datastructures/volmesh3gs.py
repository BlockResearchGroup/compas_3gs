from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import VolMesh

from compas.geometry import centroid_points
from compas.geometry import normalize_vector


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

    def vertex_normal(self, vertex):
        """Return the normal vector at the vertex as the weighted average of the
        normals of the neighboring faces.

        Parameters
        ----------
        key : int
            The identifier of the vertex.

        Returns
        -------
        list
            The components of the normal vector.
        """
        if not self.is_vertex_on_boundary(vertex):
            return

        halffaces = []
        for halfface in self.vertex_halffaces(vertex):
            if self.is_halfface_on_boundary(halfface):
                halffaces.append(halfface)

        vectors = [self.face_normal(halfface, False) for halfface in halffaces if halfface is not None]
        return normalize_vector(centroid_points(vectors))

    def vertex_update_xyz(self, vertex, new_xyz, constrained=True):

        if constrained:
            # X
            if self.vertex_attribute(vertex, 'x_fix') is False:
                self.vertex_attribute(vertex, 'x', new_xyz[0])
            # Y
            if self.vertex_attribute(vertex, 'y_fix') is False:
                self.vertex_attribute(vertex, 'y', new_xyz[1])
            # Z
            if self.vertex_attribute(vertex, 'z_fix') is False:
                self.vertex_attribute(vertex, 'z', new_xyz[2])
        else:
            self.vertex_attribute(vertex, 'x', new_xyz[0])
            self.vertex_attribute(vertex, 'y', new_xyz[1])
            self.vertex_attribute(vertex, 'z', new_xyz[2])

    # --------------------------------------------------------------------------
    # halfface
    # --------------------------------------------------------------------------

    def boundary_halfface_manifold_neighbors(self, halfface):
        nbrs = []
        cell = self.halfface_cell(halfface)
        for halfedge in self.halfface_halfedges(halfface):
            print('halfedge', halfedge)
            for face in self.edge_halffaces(halfedge):
                print('face -------------------------', face)
                if self.is_halfface_on_boundary(face):
                    print('cell', cell)
                    print('nbr_ckey', self.halfface_cell(face))

                    if self.halfface_cell(face) is not cell:
                        print('add face')
                        nbrs.append(face)
        print('nbrs', nbrs)
        return nbrs

    def boundary_halfface_manifold_neighborhood(self, hfkey, ring=1):
        nbrs = set(self.boundary_halfface_manifold_neighbors(hfkey))
        i = 1
        while True:
            if i == ring:
                break
            temp = []
            for nbr_hfkey in nbrs:
                temp += self.boundary_halfface_manifold_neighbors(hfkey)
            nbrs.update(temp)
            i += 1
        return list(nbrs - set([hfkey]))

    # --------------------------------------------------------------------------
    # cell
    # --------------------------------------------------------------------------

    def cell_pair_halffaces(self, cell_1, cell_2):
        """Given 2 ckeys, returns the interfacing halffaces, respectively.
        Parameters
        ----------
        ckey_1 : hashable
            Identifier of the cell 1.
        ckey_2 : hashable
            Identifier of the cell 2.
        Returns
        -------
        hfkey_1
            The identifier of the halfface belonging to cell 1 .
        hfkey_2
            The identifier of the halfface belonging to cell 2.
        """
        for halfface in self.cell_faces(cell_1):
            u, v, w = self.halfface_vertices(halfface)[0:3]
            nbr = self._plane[w][v][u]

            if nbr == cell_2:
                return halfface, self.halfface_opposite_halfface(halfface)

        raise KeyError

    # --------------------------------------------------------------------------
    # drawing
    # --------------------------------------------------------------------------

    # def draw(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.clear_by_name()
    #     artist.draw_faces(**kwattr)
    #     artist.draw_vertices(**kwattr)

    # def clear(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.clear_by_name()
    #     artist.clear_layer()

    # def draw_edges(self, **kwattr):
    #     artist = VolMeshArtist(self, **kwattr)
    #     artist.draw_edges(**kwattr)

    # def draw_faces(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.draw_faces(**kwattr)

    # def clear_faces(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.clear_faces(**kwattr)

    # def draw_facelabels(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.draw_facelabels(**kwattr)

    # def draw_vertices(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.draw_vertices(**kwattr)

    # def draw_vertexlabels(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.draw_vertexlabels(**kwattr)

    # def draw_edgelabels(self, **kwattr):
    #     artist = VolMeshArtist(self, layer=self.layer)
    #     artist.draw_edgelabels(**kwattr)


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
