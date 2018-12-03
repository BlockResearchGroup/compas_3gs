

__all__ = ['pair_edge_to_halfface']


def pair_edge_to_halfface(volmesh, network):
    pair_dict = {}
    for u, v in network.edges():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        pair_dict[u_hfkey] = (u, v)
    return pair_dict
