



def volmesh_select_dependent_halffaces(volmesh, hfkey):

    # dep_hfkeys = set()

    # count = 50
    # while count:
    #     count -= 1


    #     ckey = volmesh.halfface_cell(hfkey)
    #     hf_edges = volmesh.halfface_edges(hfkey)

    #     print('-------------------------------------------')
    #     print('ckey', ckey)
    #     print('hfkey', hfkey)

    #     for edge in hf_edges:
    #         u = edge[0]
    #         v = edge[1]

    #         perp_hfkey = volmesh.cell[ckey][v][u]
    #         w = volmesh.halfface_vertex_ancestor(perp_hfkey, v)

    #         nbr_ckey = volmesh.plane[u][v][w]

    #         if not nbr_ckey:
    #             break

    #         hfkey = volmesh.cell[nbr_ckey][v][u]
    #         dep_hfkeys.add(hfkey)

    # return list(dep_hfkeys)

    dependents = set(volmesh.halfface_dependent_halffaces(hfkey))
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
                hfkeys = volmesh.halfface_dependent_halffaces(dep_hfkey)
                temp += hfkeys
                seen.add(dep_hfkey)

        dependents.update(temp)
        i += 1

    if hfkey in dependents:
        dependents.remove(hfkey)

    return list(dependents)






    # dependents = set(volmesh.halfface_dependent_halffaces(hfkey))

    # count = 100
    # while count:
    #     count -= 1

    #     temp = []
    #     for dep_hfkey in dependents:
    #         temp += volmesh.halfface_dependent_halffaces(dep_hfkey)

    #     dependents.update(temp)

    # dependents.remove(hfkey)
    # return list(dependents)