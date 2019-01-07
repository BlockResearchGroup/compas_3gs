

# ------------------------------------------------------------------------------
#   planarisation
# ------------------------------------------------------------------------------

def volmesh_faces_planarise(forcediagram,
                            kmax=100,
                            tol=1e-6,
                            target_normals=None,
                            target_centres=None,
                            best_fit=False):

    for k in range(kmax):

        flatness = 0

        positions = {vkey: [] for vkey in volmesh.vertices()}

        for fkey in forcediagram.faces:

            normal = normal(face)
            centre = centroid(face)

            if fkey in target_normals:
                normal = target_normals[fkey]
            if fkey in target_centres:
                centre = target_centres[fkey]
            plane = (centre, normal)

            if best_fit:
                plane = bestfit_plane(points)

            points = project_to_plane(face, plane)



            for index, vkey in enumerate(points):
                positions[vkey].append(projections[index])


            if deviation(face) > flatness:
                flatness = deviation

        for vkey, attr in forcediagram.vertices(True):

            x, y, z = centroid_points(positions[key])
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

        if flatness < tol:
            break

    return forcediagram




