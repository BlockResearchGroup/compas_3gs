



def volmesh_select_dependent_halffaces(volmesh, hfkey):

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
