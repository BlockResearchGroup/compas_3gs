# def volmesh_planarize_faces(volmesh, count=500, tolerance=0.001):

#     while count:

#         deviation    = 0

#         new_vertices = {vkey: [] for vkey in volmesh.vertex}

#         for hfkey in volmesh.faces():
#             hf_vkeys = volmesh.halfface_vertices(hfkey)
#             points   = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]
#             plane    = bestfit_plane(points)

#             for vkey in hf_vkeys:
#                 xyz     = volmesh.vertex_coordinates(vkey)
#                 new_xyz = project_point_plane(xyz, plane)
#                 dist    = distance_point_point(xyz, new_xyz)
#                 if dist > deviation:
#                     deviation = dist
#                 new_vertices[vkey].append(new_xyz)

#         for vkey in new_vertices:
#             final_xyz = centroid_points(new_vertices[vkey])
#             volmesh.vertex_update_xyz(vkey, final_xyz)

#         if deviation < tolerance:
#             break

#         count -= 1

#     return volmesh






# simple...

def volmesh_planarise_faces(volmesh,
                            count=500,
                            tol=1e-6,
                            best_fit=False):

    while count:

        deviation    = 0

        new_vertices = {vkey: [] for vkey in volmesh.vertex}

        for hfkey in volmesh.faces():

            target_normal = volmesh.f_data[hfkey]['target_normal']
            if target_normal:
                hf_normal = volmesh.halfface_oriented_normal(hfkey)
            hf_center = volmesh.halfface_center(hfkey)

            hf_vkeys  = volmesh.halfface_vertices(hfkey)
            points    = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]

            plane     = (hf_center, hf_normal)
            if best_fit:
                plane   = bestfit_plane(points)

            for vkey in hf_vkeys:
                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                dist    = distance_point_point(xyz, new_xyz)
                if dist > deviation:
                    deviation += dist
                new_vertices[vkey].append(new_xyz)

        for vkey in new_vertices:
            final_xyz = centroid_points(new_vertices[vkey])
            volmesh.vertex_update_xyz(vkey, final_xyz)

        if deviation < tol:
            break

        count -= 1

    return volmesh











# with arearisation built in....

def volmesh_planarise_faces(volmesh,
                            count=500,
                            tol=1e-6,
                            best_fit=False):

    while count:

        deviation    = 0

        new_vertices = {vkey: [] for vkey in volmesh.vertex}

        for hfkey in volmesh.faces():

            target_normal = volmesh.f_data[hfkey]['target_normal']
            if target_normal:
                hf_normal = volmesh.halfface_oriented_normal(hfkey)
            hf_center = volmesh.halfface_center(hfkey)

            hf_vkeys  = volmesh.halfface_vertices(hfkey)
            points    = [volmesh.vertex_coordinates(vkey) for vkey in hf_vkeys]

            target_area = volmesh.f_data[hfkey]['target_area']
            if target_area:
                area        = volmesh.halfface_oriented_area(hfkey)
                deviation   += abs(target_area - area)
                s           = (target_area / area) ** 0.5
                points      = scale_polygon(points, s)

            plane     = (hf_center, hf_normal)
            if best_fit:
                plane   = bestfit_plane(points)

            for vkey in hf_vkeys:
                xyz     = volmesh.vertex_coordinates(vkey)
                new_xyz = project_point_plane(xyz, plane)
                dist    = distance_point_point(xyz, new_xyz)
                if dist > deviation:
                    deviation += dist
                new_vertices[vkey].append(new_xyz)

        for vkey in new_vertices:
            final_xyz = centroid_points(new_vertices[vkey])
            volmesh.vertex_update_xyz(vkey, final_xyz)

        if deviation < tol:
            break

        count -= 1

    return volmesh
