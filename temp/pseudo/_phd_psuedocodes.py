

# ------------------------------------------------------------------------------
#   constructor - cell --> egi
# ------------------------------------------------------------------------------

def egi_from_cell(volmesh, ckey):

    egi = Mesh()

    egi.attributes['name']   = ckey
    egi.attributes['origin'] = volmesh.cell_cente_of_mass(ckey)

    for hfkey in volmesh.cell_halffaces(ckey):
        normal  = volmesh.halfface_oriented_normal(hfkey)
        x, y, z = add_vectors(origin, normal)
        egi.add_vertex(key=hfkey, x=x, y=y, z=z)

    for vkey in volmesh.cell_vertices(ckey):
        face = volmesh.cell_vertex_halffaces(ckey, vkey)
        egi.add_face(face, fkey=vkey)

    return egi


# ------------------------------------------------------------------------------
#   oriented normal
# ------------------------------------------------------------------------------

def oriented_normal_polygon(points, unitized=True):

    p = len(points)
    assert p > 2, "At least three points required"

    w          = centroid_points(points)

    normal_sum = (0, 0, 0)
    for i in range(-1, len(points) - 1):
        u          = points[i]
        v          = points[i + 1]
        uv         = subtract_vectors(v, u)
        vw         = subtract_vectors(w, v)
        normal     = scale_vector(cross_vectors(uv, vw), 0.5)
        normal_sum = add_vectors(normal_sum, normal)
    if not unitized:
        return normal_sum
    return normalize_vector(normal_sum)


# ------------------------------------------------------------------------------
#   cell halfface push
# ------------------------------------------------------------------------------

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


# ------------------------------------------------------------------------------
#   split cell vertex
# ------------------------------------------------------------------------------

def cell_halfface_vertices_split(volmesh, hfkey):

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










# ------------------------------------------------------------------------------
#   planarisation
# ------------------------------------------------------------------------------

def volmesh_faces_planarise(volmesh,
                            kmax=100,
                            tol=1e-6,
                            target_normals=None,
                            target_centres=None,
                            target_areas=None):

    for k in range(kmax):

        flatness = 0

        positions = {vkey: [] for vkey in volmesh.vertices()}

        for fkey in volmesh.faces():

            centre, normal = bestfit_plane(points)
            if fkey in target_normals:
                normal = target_normals[fkey]
            if fkey in target_centres:
                centre = target_centres[fkey]
            plane       = (centre, normal)

            vertices    = volmesh.halfface_vertices(fkey)
            points      = [volmesh.vertex_coordinates(vkey) for vkey in vertices]
            projections = project_points_plane(points, plane)


            if fkey in target_areas:
                projections = scale_polygon(projections, target_areas[fkey])


            for index, vkey in enumerate(vertices):
                positions[vkey].append(projections[index])

            deviation = halfface_flatness(volmesh, fkey)
            if deviation > flatness:
                flatness = deviation

        for vkey, attr in volmesh.vertices(True):
            if key in fixed:
                continue

            x, y, z = centroid_points(positions[key])
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

        if flatness < tol:
            break

    return volmesh