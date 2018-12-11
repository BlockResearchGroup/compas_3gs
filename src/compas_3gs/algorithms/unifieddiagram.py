from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas
import compas_rhino

from compas.geometry import convex_hull

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_3gs.utilities import pair_uv_to_hf


__author__     = ['Juney Lee']
__copyright__  = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'juney.lee@arch.ethz.ch'


__all__ = ['volmesh_ud',
           'cellnetwork_ud']


def volmesh_ud(volmesh,
               network,
               scale=0.5):
    """Computes temporary vertex coordinates for every halfface, for the visualisation of the unified diagram.

    Parameters
    ----------
    volmesh : VolMesh
        A volmesh object representing a polyhedral force diagram.
    network : Network
        A network object representing a polyhedral form diagram.

    Returns
    -------
    dictionary of dictionaries
        A dictionary of dictionaries: hfkey-{vkey: (x, y, z)}.

    Notes
    -----


    """

    halffaces = {}

    # --------------------------------------------------------------------------
    #   1. if scale == 0, the unified diagram IS the polyhedral force diagram.
    # --------------------------------------------------------------------------
    if scale == 0:
        return hf_xyz

    volmesh_center = volmesh.datastructure_centroid()
    network_center = network.datastructure_centroid()
    translation    = subtract_vectors(volmesh_center, network_center)

    # --------------------------------------------------------------------------
    #   2. get base points
    # --------------------------------------------------------------------------
    base_xyz = {}
    for vkey in network.vertex:
        init_xyz       = network.vertex_coordinates(vkey)
        base_xyz[vkey] = add_vectors(init_xyz, translation)

    # --------------------------------------------------------------------------
    #   3. compute scaled halffaces
    # --------------------------------------------------------------------------
    for ckey in volmesh.cell:
        cell_hfs = volmesh.cell_halffaces(ckey)
        for hfkey in cell_hfs:
            hf_vertices = {}
            for vkey in volmesh.halfface_vertices(hfkey):
                xyz = volmesh.vertex_coordinates(vkey)
                arm = subtract_vectors(xyz, base_xyz[vkey])
                arm = scale_vector(arm, scale)
                hf_vertices[vkey] = add_vectors(base_xyz, arm)
            halffaces[hfkey] = hf_vertices

    # --------------------------------------------------------------------------
    #   4. compute prism faces
    # --------------------------------------------------------------------------
    prism_faces = {}

    for u, v in network.edges():

        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        u_pts   = halffaces[u_hfkey].values()
        v_pts   = halffaces[v_hfkey].values()

        pt_list = u_pts + v_pts

        prism   = convex_hull(u_pts + v_pts)  # face as indices of pt_list

        face_list = []

        for face in prism:
            # face is a list ...
            face_xyz = [pt_list[i] for i in face]  # get face xyz in order
            face_list.append(face_xyz)

        prism_faces[(u,v)] = face_list


    return halffaces, prism_faces


def cellnetwork_ud(cellnetwork):
    pass





