from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import mesh_dual

from compas.geometry import dot_vectors
from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point
from compas.geometry import intersection_line_plane

from compas_3gs.diagrams import EGI


__author__    = 'Juney Lee'
__copyright__ = 'Copyright 2019, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'juney.lee@arch.ethz.ch'


__all__ = ['cell_split_indet_face_vertices',
           'cell_collapse_short_edge',

           'cell_relocate_face',
           'cell_face_subdivide_barycentric',
           'cell_merge_coplanar_adjacent_faces',
           'check_cell_convexity']


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell vertices
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_split_indet_face_vertices(cell, fkey):
    """Split all indeterminate vertices of a cell face.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    fkey : hashable
        Identifier of the face.

    Returns
    -------
    Cell
        Updated cell.

    Notes
    -----
    An indeterminate vertex is defined as a vertex with degree or valency of 3 or greater.

    """
    egi = mesh_dual(cell, EGI)

    f_vkeys      = cell.face_vertices(fkey)
    egi_nbr_vkeys = egi.vertex_neighbors(fkey)

    for egi_fkey in f_vkeys:

        fkeys = egi.face_vertices(egi_fkey)
        i     = fkeys.index(fkey)
        fkeys = fkeys[i:] + fkeys[:i]

        egi_face_vertices = [key for key in fkeys if key not in egi_nbr_vkeys + [fkey]]

        vkey_del = egi_fkey
        x, y, z  = cell.vertex_coordinates(vkey_del)

        for vkey in egi_face_vertices:

            f, g = egi.mesh_split_face(vkey_del, fkey, vkey)

            cell.delete_vertex(vkey_del)

            cell.add_vertex(key=f, x=x, y=y, z=z)
            cell.add_vertex(key=g, x=x, y=y, z=z)

            for new_fkey in fkeys:
                new_vkeys = egi.vertex_faces(new_fkey, ordered=True)
                cell.add_face(new_vkeys, fkey=new_fkey)
            vkey_del = g

    return cell


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell edges
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_collapse_short_edge(cell, u, v, min_length=0.1):
    """Collapse short edges of a cell.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    u : hashable
        The key of the start vertex.
    v : hashable
        The key of the end vertex.
    min_length : float
        Minimum length of edges to be collapsed.

    Returns
    -------
    cell : Mesh
        Updated cell.

    """
    sp   = cell.vertex_coordinates(u)
    ep   = cell.vertex_coordinates(v)
    dist = distance_point_point(sp, ep)

    if dist < min_length:
        mp = midpoint_point_point(sp, ep)
        cell.vertex_attributes(u, 'xyz', mp)
        cell.vertex_attributes(v, 'xyz', mp)

    return cell


# ******************************************************************************
# ******************************************************************************
# ******************************************************************************
#
#   cell face operations
#
# ******************************************************************************
# ******************************************************************************
# ******************************************************************************


def cell_cull_zero_faces(cell):
    pass


def cell_relocate_face(cell, fkey, xyz, normal):
    """Relocate the face of a mesh.

    Parameters
    ----------
    cell : Mesh
        Cell as a mesh object.
    fkey : hashable
        Identifier of the face.
    xyz : tuple
        xyz coordinates of the new target plane.
    normal : tuple
        Target normal vector.

    Returns
    -------
    cell : Mesh
        Updated cell.
    """

    cell_split_indet_face_vertices(cell, fkey)

    vkeys = cell.face_vertices(fkey)

    # new target plane for the face
    plane = (xyz, normal)

    # neighboring edges
    edges = {}
    for u in vkeys:
        for v in cell.vertex_neighbors(u):
            if v not in vkeys:
                edges[u] = v

    for u in edges:
        line = cell.edge_coordinates(u, edges[u])
        it   = intersection_line_plane(line, plane)
        cell.vertex_update_xyz(u, it, constrained=False)

    return cell


def cell_merge_coplanar_adjacent_faces(cell, tol=0.001):

    initial_faces = [key for key in cell.face]
    current_faces = [key for key in cell.face]

    for fkey in initial_faces:

        if fkey in current_faces:
            normal = cell.face_normal(fkey)

            faces_to_delete = []

            for nbr_fkey in cell.face_neighbours(fkey):
                nbr_normal = cell.face_normal(nbr_fkey)
                dot = dot_vectors(normal, nbr_normal)
                if 1 - dot < tol:
                    faces_to_delete.append(nbr_fkey)

            if faces_to_delete:
                new_halfedges = cell.face_halfedges(fkey)
                for del_fkey in faces_to_delete:
                    for u, v in cell.face_halfedges(del_fkey):
                        if (v, u) in new_halfedges:
                            new_halfedges.remove((v, u))
                        else:
                            new_halfedges.append((u, v))

                new_face = list(new_halfedges[0])

                for i in range(1, len(new_halfedges)):
                    u, v = new_halfedges[i]
                    if u in new_face:
                        index = new_face.index(u)
                        new_face.insert(index + 1, v)
                    else:
                        index = new_face.index(v)
                        new_face.insert(index, u)

                for key in faces_to_delete:
                    cell.delete_face(key)
                    current_faces.remove(key)

                cell.add_face(vertices=new_face, fkey=fkey)

    return cell


def cell_face_subdivide_barycentric(cell, fkey, cls=None):
    # the cell should be a tetrahedral / pyramid shape polyhedron? 
    from compas_3gs.datastructures import VolMesh3gs
    if cls is None:
        cls = VolMesh3gs()

    f_center = cell.face_centroid(fkey) 
    print(f_center, 'face_center')
    vertices_dict = {}
    vertices = []
    for vkey in cell.vertices():
        if cell.vertex_coordinates(vkey) not in vertices:
            vertices_dict[vkey] = len(vertices)
            vertices.append(cell.vertex_coordinates(vkey))
        else:
            vertices_dict[vkey] = vertices.index(cell.vertex_coordinates(vkey))

    f_center_key = len(vertices)  # vertex key of the face center
    vertices.append(f_center)

    print(len(vertices))

    cells = []
    descendant = {i: j for i, j in cell.face_halfedges(fkey)}
    # ancestor = {j: i for i, j in cell.face_halfedges(fkey)}

    f_vkeys = cell.face_vertices(fkey)
    other_vkeys = [vkey for vkey in cell.vertices() if vkey not in f_vkeys]
    print(other_vkeys)

    if len(other_vkeys) == 1:
        end_key = other_vkeys[0]
        for vkey in f_vkeys:
            d = descendant[vkey]
            face_1 = [vertices_dict[vkey], vertices_dict[d], f_center_key]
            face_2 = [vertices_dict[d], vertices_dict[vkey], vertices_dict[end_key]]
            face_3 = [vertices_dict[vkey], f_center_key, vertices_dict[end_key]]
            face_4 = [f_center_key, vertices_dict[d], vertices_dict[end_key]]
            cell = [face_1, face_2, face_3, face_4]
            cells.append(cell)

    print(cells)
    return cls.from_vertices_and_cells(vertices, cells)


def check_cell_convexity(cell):
    """cell: mesh / mesh3gs
    check the convexity of the cell
    check that all the other vertices lie on the same side of that face.
    by calculating the face normal vector and computing the dot-product for each vector from one vertex on the face to all the others
    The signs must be the same.

    """
    import compas.geometry as cg
    vkeys = cell.vertices()
    for fkey in cell.faces():
        f_normal = cell.face_normal(fkey)
        f_vkeys = cell.face_vertices(fkey)
        f_v_xyz = cell.vertex_coordinates(f_vkeys[0]) # one vertex on the face
        other_vkeys = [vkey for vkey in vkeys if vkey not in f_vkeys]
        for i, v in enumerate(other_vkeys):
            v_xyz = cell.vertex_coordinates(f_vkeys[v])
            vec = cg.Vector.from_start_end(f_v_xyz, v_xyz)
            dot = dot_vectors(f_normal, vec)
            if i == 0:
                dot_0 = dot
            else:
                if dot_0 * dot < 0:
                    return "This is not a convex cell."
    print("This is a convex cell.")
    return True


def cells_face_subdivide_barycentric(cell, fkey, cls=None):
    """Volmesh face subdivision
    """
    raise NotImplementedError



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
