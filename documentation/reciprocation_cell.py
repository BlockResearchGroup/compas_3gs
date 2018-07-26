def volmesh_reciprocate(volmesh,
                        formdiagram,
                        weight,
                        count=50,
                        min_edge,
                        max_edge,
                        tolerance=0.001):

    target_normals = {}
    halfface_uv    = {}
    for u, v in formdiagram.edges_iter():
        u_hfkey, v_hfkey = volmesh.cell_pair_hfkeys(u, v)
        face_normal   = scale_vector(volmesh.halfface_normal(u_hfkey), weight)
        edge_vector   = scale_vector(formdiagram.edge_vector(u, v), 1 - weight)
        target_vector = normalize_vector(add_vectors(face_normal, edge_vector))
        target_normals[u_hfkey] = target_vector
        halfface_uv[u_hfkey]    = (u, v)

    while count:

        volmesh_planarize_faces(volmesh, count=1, target_normals=target_normals)

        deviation = 0

        new_formdiagram_xyz = {vkey: [] for vkey in formdiagram.vertex}

        for hfkey in halfface_uv:

            u, v          = halfface_uv[hfkey]
            target_normal = target_normals[hfkey]

            edge_vector   = formdiagram.edge_vector(u, v, unitized=False)
            dot_v         = dot_vectors(normalize_vector(edge_vector), target_normal)
            if dot_v < 0:
                target_normal = scale_vector(target_normal, -1)

            perp_check = abs(1 - abs(dot_v))
            if perp_check > deviation:
                deviation = perp_check

            dist = length_vector(edge_vector)
            if dist < min_edge:
                dist = min_edge
            if dist > max_edge:
                dist = max_edge

            u_xyz = formdiagram.vertex_coordinates(u)
            v_xyz = formdiagram.vertex_coordinates(v)

            new_u_xyz = add_vectors(v_xyz, scale_vector(target_normal, -1 * dist))
            new_formdiagram_xyz[u].append(new_u_xyz)

            new_v_xyz = add_vectors(u_xyz, scale_vector(target_normal, dist))
            new_formdiagram_xyz[v].append(new_v_xyz)

        for vkey in new_formdiagram_xyz:
            if new_formdiagram_xyz[vkey]:
                initial_xyz = formdiagram.vertex_coordinates(vkey)
                final_xyz   = centroid_points(new_formdiagram_xyz[vkey])
                formdiagram.vertex_update_xyz(vkey, final_xyz)

        if deviation < tolerance:
            break

        count -= 1

    return volmesh, formdiagram
