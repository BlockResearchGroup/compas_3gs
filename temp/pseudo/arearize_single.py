

def arearize_halfface(volmesh, hfkey, target, tol=1e-6):

    cell_split_halfface_vertices(volmesh, hfkey)

    hf_center     = volmesh.halfface_center(hfkey)
    hf_normal     = volmesh.halfface_oriented_normal(hfkey)
    hf_area       = volmesh.halfface_oriented_area(hfkey)

    move_dir = _get_move_direction(volmesh, hfkey)

    gr = (math.sqrt(5) + 1) / 2

    a  = 0
    b  = abs(hf_area - target)
    c  = b - (b - a) / gr
    d  = a + (b - a) / gr

    while abs(c - d) > tol:

        move_c   = c * move_dir
        center_c = add_vectors(hf_center, scale_vector(hf_normal, move_c))
        area_c   = evaluate_trial_face_area(volmesh, hfkey, center_c)
        eval_c   = area_c - target

        move_d   = d * move_dir
        center_d = add_vectors(hf_center, scale_vector(hf_normal, move_d))
        area_d   = evaluate_trial_face_area(volmesh, hfkey, center_d)
        eval_d   = area_d - target

        if abs(eval_c) < abs(eval_d):
            b = d

        else:
            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

    z          = move_dir * (b + a) / 2
    new_center = add_vectors(hf_center, scale_vector(hf_normal, z))

    cell_halfface_push(volmesh, hfkey, new_center)

    return volmesh


def cell_halfface_push(volmesh, hfkey, z):

    hf_center = volmesh.halfface_center(hfkey)
    hf_normal = volmesh.halfface_oriented_normal(hfkey)
    hf_vkeys  = volmesh.halfface_vertices(hfkey)

    xyz       = add_vector(hf_center, scale_vector(hf_normal, z))
    new_plane = (xyz, hf_normal)

    edges = {}
    for u in hf_vkeys:
        u_nbrs = volmesh.vertex_neighbours(u)
        for v in u_nbrs:
            if v not in hf_vkeys:
                edges[u] = v

    for u in edges:
        v     = edges[u]
        u_xyz = volmesh.vertex_coordinates(u)
        v_xyz = volmesh.vertex_coordinates(v)
        line  = (u_xyz, v_xyz)
        it    = intersection_line_plane(line, new_plane)
        volmesh.vertex_update_xyz(u, it, constrained=False)

    return volmesh



def cell_split_halfface_vertices(volmesh, hfkey):

    ckey          = volmesh.halfface_cell(hfkey)
    hf_vkeys      = volmesh.halfface_vertices(hfkey)
    egi           = volmesh.c_data[ckey]['egi']
    egi_nbr_vkeys = egi.vertex_neighbours(hfkey)

    for egi_fkey in hf_vkeys:
        hfkeys      = egi.face[egi_fkey]
        n           = hfkeys.index(hfkey)
        hfkeys      = hfkeys[n:] + hfkeys[:n]
        egi_f_vkeys = [key for key in hfkeys if key not in egi_nbr_vkeys + [hfkey]]
        fkey        = egi_fkey
        x, y, z     = volmesh.vertex_coordinates(egi_fkey)

        for vkey in egi_f_vkeys:
            f, g = egi.mesh_split_face(fkey, hfkey, vkey)
            volmesh.add_vertex(key=f, x=x, y=y, z=z)
            volmesh.add_vertex(key=g, x=x, y=y, z=z)

            for new_hfkey in hfkeys:
                new_vkeys = egi.vertex_faces(new_hfkey, ordered=True)
                volmesh.add_halfface(new_vkeys[::-1], fkey=new_hfkey)

            volmesh.cell_vertex_delete(fkey)
            fkey = g

    return volmesh
