from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import scale_vector

from compas_3gs.utilities import datastructure_centroid


__all__ = [
    'point_reflection'
]


def point_reflection(datastructure):
    """Inverts a datastructure through its centroid.

    Parameters
    ----------
    datastructure
        A network, mesh or volmesh object.

    Returns
    -------
        The datastructure with new vertex coordinates.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Point_reflection

    """
    center = datastructure_centroid(datastructure)

    for vkey in datastructure.vertex:
        xyz     = datastructure.vertex_coordinates(vkey)
        vector  = scale_vector(subtract_vectors(center, xyz), 2)
        new_xyz = add_vectors(xyz, vector)
        datastructure.vertex_update_xyz(vkey, new_xyz, constrained=False)
