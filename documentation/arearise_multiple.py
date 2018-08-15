def arearise_halffaces(volmesh,
                       target_dict,
                       count=100,
                       tol=1e-6):

    iteration = 0
    deviation = 0


    while count:





        new_xyz = dict((vkey, []) for vkey in cell.vertex)


        for hfkey in target_dict:

            target_area = target_dict[hfkey]
            area = current_area(hfkey)

            s = (target_area / area) ** 0.5


            new_face = scale_face(face, s)






        for fkey in cell.face:
            face = cell.face[fkey]

            s = (target_area(face) / current_area(face)) ** 0.5
            new_face = scale_face(face, s)

            if is_face_dapative(face):
                project_face(new_face, best_fit_plane(new_face))
            else:
                project_face(new_face, (initial_normal(face), centroid(face)))
        for vkey in new_face:
            new_xyz[vkey].append(new_face[vkey])
        for vkey in new_xyz:
            final_xyz = sum_avg_xyz(new_xyz, vkey)
            cell.update_vertex_coordinates(vkey, final_xyz)



        volmesh_planarise_faces(volmesh, count=1)


        if iteration == count:
            break


        iterations += 1




    return volmesh