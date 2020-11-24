from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import convex_hull
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas.utilities import geometric_key


__all__ = ['volmesh_ud',
           'cellnetwork_ud']


def volmesh_ud(volmesh,
               network,
               scale=0.5):
    """Computes temporary vertex coordinates for every halfface of a volmesh, for the visualisation of the unified diagram.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object representing a polyhedral force diagram.
    network : Network
        A network object representing a polyhedral form diagram.
    scale : float
        Unified diagram scale factor,

    Returns
    -------
    halffaces : dictionary
        A dictionary of dictionaries: hfkey-{vkey: (x, y, z)}.
    prisms : dictionary
        A dictinoary of dictinoaries: uv - [face coordinates]

    Raises
    ------
    Exception
        If scale is 0, which means the unified diagram is equivalent to the polyhedral force diagram.
    Exception
        If scale is 0, which means the unified diagram is equivalent to the polyhedral form diagram.

    Notes
    -----
    - The prisms are implemented as convex hull of two halffaces for simplicity and to resolve any small geometric errors.
    - Unified diagram with a scale of 0 is equivalent to the polyhedral force diagram, while a scale of 1 is equivalent to the polyhedral form diagram.

    """

    # --------------------------------------------------------------------------
    #   0. evaluate unified diagram scale
    # --------------------------------------------------------------------------
    if scale == 0:
        raise Exception("A unified diagram with a scale of 0 is equivalent to the polyhedral force diagram.")

    if scale == 1:
        raise Exception("A unified diagram with a scale of 1 is equivalent to the polyhedral form diagram.")

    assert 0 < scale and scale < 1, "Scale needs to be between 0 and 1."

    # --------------------------------------------------------------------------
    #   1. current positions of diagrams
    # --------------------------------------------------------------------------
    volmesh_center = volmesh.centroid()
    network_center = network.datastructure_centroid()
    translation = subtract_vectors(volmesh_center, network_center)

    # --------------------------------------------------------------------------
    #   2. get base points
    # --------------------------------------------------------------------------
    base_xyz = {}

    for vkey in network.nodes():
        init_xyz = network.node_coordinates(vkey)
        base_xyz[vkey] = add_vectors(init_xyz, translation)

    # --------------------------------------------------------------------------
    #   3. compute scaled halffaces
    # --------------------------------------------------------------------------
    halffaces = {}

    for ckey in volmesh.cells():
        cell_hfs = volmesh.cell_faces(ckey)
        for hfkey in cell_hfs:
            hf_vertices = {}
            for vkey in volmesh.halfface_vertices(hfkey):
                xyz = volmesh.vertex_coordinates(vkey)
                arm = scale_vector(subtract_vectors(xyz, base_xyz[ckey]), scale)
                hf_vertices[vkey] = add_vectors(base_xyz[ckey], arm)
            halffaces[hfkey] = hf_vertices

    scaled_halffaces = {}
    cells = {}

    for cell in volmesh.cells():
        gkey_xyz = {}
        faces = []

        for face in volmesh.cell_faces(cell):
            new_face = []
            scaled_face_xyz = []
            for vertex in volmesh.face_vertices(face):
                xyz = volmesh.vertex_coordinates(vertex)
                arm = scale_vector(subtract_vectors(xyz, base_xyz[cell]), scale)
                scaled_xyz = add_vectors(base_xyz[cell], arm)
                gkey = geometric_key(scaled_xyz)
                gkey_xyz[gkey] = scaled_xyz
                new_face.append(gkey)
                scaled_face_xyz.append(scaled_xyz)
            scaled_halffaces[face] = scaled_face_xyz
            faces.append(new_face)

        gkey_index = dict((gkey, index) for index, gkey in enumerate(gkey_xyz))
        vertices = [list(xyz) for gkey, xyz in gkey_xyz.items()]
        scaled_faces = [[gkey_index[gkey] for gkey in face] for face in faces]




        cells[cell] = {'vertices': vertices, 'faces': scaled_faces}

    # cells = {}
    # for cell in volmesh.cells():
    #     vertices = volmesh.cell_vertices(cell)
    #     faces = volmesh.cell_faces(cell)
    #     vertex_index = dict((vertex, index) for index, vertex in enumerate(vertices))
    #     scaled_vertices = []
    #     for vertex in vertices:
    #         xyz = volmesh.vertex_coordinates(vertex)
    #         arm = scale_vector(subtract_vectors(xyz, base_xyz[cell]), scale)
    #         scaled_vertices.append(add_vectors(base_xyz[cell], arm))
    #     faces = [[vertex_index[vertex] for vertex in volmesh.halfface_vertices(face)] for face in faces]
    #     cells[cell] = {'vertices': scaled_vertices, 'faces': faces}

    # --------------------------------------------------------------------------
    #   4. compute prism faces
    # --------------------------------------------------------------------------
    # prism_faces = {}

    prism_cells = {}

    for u, v in network.edges():
        u_hfkey, v_hfkey = volmesh.cell_pair_halffaces(u, v)
        u_pts = scaled_halffaces[u_hfkey]
        v_pts = scaled_halffaces[v_hfkey]
        pts = u_pts + v_pts
        prism = convex_hull(pts)  # face as indices of pt_list
        prism_cells[(u, v)] = {'vertices': pts, 'faces': prism}

    # for u, v in network.edges():
    #     u_hfkey, v_hfkey = volmesh.cell_pair_halffaces(u, v)
    #     u_pts = halffaces[u_hfkey].values()
    #     v_pts = halffaces[v_hfkey].values()
    #     pt_list = u_pts + v_pts
    #     prism = convex_hull(u_pts + v_pts)  # face as indices of pt_list
    #     face_list = []
    #     for face in prism:
    #         face_xyz = [pt_list[i] for i in face]  # get face xyz in order
    #         face_list.append(face_xyz)
    #     prism_faces[(u, v)] = face_list
    #     prism_cells[(u, v)] = {'vertices': pt_list, 'faces': face_list}

    # --------------------------------------------------------------------------

    # return halffaces, prism_faces
    return cells, prism_cells


def cellnetwork_ud(cellnetwork):
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
